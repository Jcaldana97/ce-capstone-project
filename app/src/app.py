import structlog
from flask import Flask, request, g, render_template
import uuid
import time
import threading
import os
import socket
import urllib.request
import boto3
from botocore.exceptions import ClientError


# =========================================================
# Configuration
# =========================================================

CART_ABANDONMENT_TIMEOUT = 60

CART_MONITORING_INTERVAL = 30

CARTS_TABLE_NAME = os.getenv("CARTS_TABLE_NAME", "capstone-project-database")
CART_TTL_BUFFER_SECONDS = 300  # keep abandoned/completed carts around briefly for metrics/debugging

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
carts_table = dynamodb.Table(CARTS_TABLE_NAME)


# =========================================================
# Structured logging
# =========================================================

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.WriteLoggerFactory(
        file=open("application.log", "a")
    ),
)

logger = structlog.get_logger()


# =========================================================
# Flask
# =========================================================

app = Flask(__name__)

# Business metrics are kept in memory and written to application.log
# through structlog. No CloudWatch API is called by this application.
business_metrics = {
    "tickets_sold": 0,
    "completed_orders": 0,
    "cancelled_orders": 0,
    "tickets_by_band_zone": {},
    "tickets_by_band": {},
}

metrics_lock = threading.Lock()


# =========================================================
# EC2 Instance Metadata
# =========================================================

def get_ec2_metadata(path):

    try:

        # -------------------------------------------------
        # Request IMDSv2 token
        # -------------------------------------------------

        token_request = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={
                "X-aws-ec2-metadata-token-ttl-seconds": "21600"
            }
        )

        with urllib.request.urlopen(
            token_request,
            timeout=1
        ) as response:

            token = response.read().decode()


        # -------------------------------------------------
        # Request metadata
        # -------------------------------------------------

        metadata_request = urllib.request.Request(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers={
                "X-aws-ec2-metadata-token": token
            }
        )

        with urllib.request.urlopen(
            metadata_request,
            timeout=1
        ) as response:

            return response.read().decode()


    except Exception:

        return None


def get_instance_id():

    instance_id = get_ec2_metadata(
        "instance-id"
    )

    if instance_id:

        return instance_id


    instance_id = os.getenv(
        "EC2_INSTANCE_ID"
    )

    if instance_id:

        return instance_id


    return socket.gethostname()


def get_availability_zone():

    availability_zone = get_ec2_metadata(
        "placement/availability-zone"
    )

    if availability_zone:

        return availability_zone


    availability_zone = os.getenv(
        "AWS_AVAILABILITY_ZONE"
    )

    if availability_zone:

        return availability_zone


    return "local"


# =========================================================
# Business Metrics
# =========================================================

def record_business_metrics(event, *, band=None, zone=None, tickets=0):
    """Update metrics and write them to application.log via structlog."""
    with metrics_lock:
        if event == "order_completed":
            business_metrics["tickets_sold"] += tickets
            business_metrics["completed_orders"] += 1

            if band:
                business_metrics["tickets_by_band"][band] = (
                    business_metrics["tickets_by_band"].get(band, 0) + tickets
                )

                if zone:
                    by_zone = business_metrics["tickets_by_band_zone"]
                    if band not in by_zone:
                        by_zone[band] = {}
                    by_zone[band][zone] = (
                        by_zone[band].get(zone, 0) + tickets
                    )

        elif event == "order_cancelled":
            business_metrics["cancelled_orders"] += 1

        total_orders = (
            business_metrics["completed_orders"]
            + business_metrics["cancelled_orders"]
        )

        cancellation_rate = (
            business_metrics["cancelled_orders"] / total_orders * 100
            if total_orders else 0
        )

        logger.info(
            "business_metric",
            metric_name="TicketsSoldSoFar",
            value=business_metrics["tickets_sold"],
        )
        logger.info(
            "business_metric",
            metric_name="CompletedOrders",
            value=business_metrics["completed_orders"],
        )
        logger.info(
            "business_metric",
            metric_name="CancelledOrders",
            value=business_metrics["cancelled_orders"],
        )
        logger.info(
            "business_metric",
            metric_name="CartAbandonmentRate",
            value=round(cancellation_rate, 2),
            unit="Percent",
        )

        for metric_band, zones in business_metrics["tickets_by_band_zone"].items():
            for metric_zone, metric_tickets in zones.items():
                logger.info(
                    "business_metric",
                    metric_name="TicketsSoldByBandAndZone",
                    band=metric_band,
                    zone=metric_zone,
                    value=metric_tickets,
                )

        for metric_band, metric_tickets in business_metrics["tickets_by_band"].items():
            logger.info(
                "business_metric",
                metric_name="TicketsSoldByBand",
                band=metric_band,
                value=metric_tickets,
            )


def cancel_cart(cart_id, correlation_id=None, reason="manual_cancel"):
    now = int(time.time())
    try:
        carts_table.update_item(
            Key={"cart_id": cart_id},
            UpdateExpression="SET #status = :abandoned, updated_at = :now",
            ConditionExpression="attribute_exists(cart_id) AND #status = :active",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":abandoned": "abandoned",
                ":active": "active",
                ":now": now,
            },
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            existing = carts_table.get_item(Key={"cart_id": cart_id}).get("Item")
            if not existing:
                return False, "cart not found"
            return False, f"cart is already {existing['status']}"
        logger.error("cart_cancel_failed", correlation_id=correlation_id,
                     cart_id=cart_id, error=str(exc))
        return False, "internal error"

    logger.info("cart_abandoned", correlation_id=correlation_id, cart_id=cart_id, reason=reason)
    record_business_metrics("order_cancelled")
    return True, None


# =========================================================
# Cart Monitoring
# =========================================================

def monitor_carts():
    while True:
        try:
            cutoff = int(time.time()) - CART_ABANDONMENT_TIMEOUT
            newly_abandoned = 0

            response = carts_table.query(
                IndexName="status-updated_at-index",
                KeyConditionExpression="#status = :active AND updated_at <= :cutoff",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={":active": "active", ":cutoff": cutoff},
            )

            for cart in response.get("Items", []):
                cancelled, _ = cancel_cart(cart["cart_id"], reason="timeout_monitor")
                if cancelled:
                    newly_abandoned += 1

            logger.info("cart_abandonment_metric", metric_name="CartAbandonmentRate",
                        newly_abandoned=newly_abandoned)

        except Exception as exc:
            logger.error("cart_monitoring_failed", error=str(exc))

        time.sleep(CART_MONITORING_INTERVAL)


# =========================================================
# Start background cart monitoring
# =========================================================

monitor_thread = threading.Thread(
    target=monitor_carts,
    daemon=True
)

monitor_thread.start()


# =========================================================
# Request Timing
# =========================================================

@app.before_request
def start_timer():

    g.start_time = time.time()


@app.after_request
def record_request_latency(response):

    duration_ms = (
        time.time() -
        g.start_time
    ) * 1000


    logger.info(
        "request_completed",
        path=request.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=round(
            duration_ms,
            2
        )
    )


    return response


# =========================================================
# UI
# =========================================================

@app.route("/ui")
def ui():

    return render_template(
        "index.html"
    )


# =========================================================
# Home
# =========================================================

@app.route("/")
def index():

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )


    logger.info(
        "request_received",
        correlation_id=correlation_id,
        path="/",
        method=request.method
    )


    return {
        "message": "Concert Ticket Service",
        "correlation_id": correlation_id
    }


# =========================================================
# Health
# =========================================================

@app.route("/health")
def health():

    logger.info(
        "health_check",
        status="healthy"
    )


    return {
        "status": "healthy"
    }


# =========================================================
# EC2 Instance Information
# =========================================================

@app.route("/instance-info")
def instance_info():

    instance_id = get_instance_id()

    availability_zone = get_availability_zone()


    logger.info(
        "instance_information_requested",
        instance_id=instance_id,
        availability_zone=availability_zone
    )


    return {
        "instance_id": instance_id,
        "availability_zone": availability_zone
    }


# =========================================================
# Create Internal Cart
#
# The UI does not expose the cart concept.
# It is maintained internally for abandonment monitoring.
#
# IMPORTANT:
# No email, name, bank account or other personal information
# is logged here.
# =========================================================

@app.route("/cart", methods=["POST"])
def create_cart():

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )


    data = request.get_json() or {}


    cart_id = (
        f"cart-{uuid.uuid4().hex[:8]}"
    )


    now = time.time()


    cart = {

        "cart_id":
            cart_id,

        "user_id":
            data.get("user_id"),

        "items":
            data.get("items", 0),

        "created_at":
            now,

        "updated_at":
            now,

        "status":
            "active"

    }


    now = int(time.time())

    cart = {
        "cart_id": cart_id,
        "user_id": data.get("user_id"),
        "items": data.get("items", 0),
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "ttl": now + CART_ABANDONMENT_TIMEOUT + CART_TTL_BUFFER_SECONDS,
    }

    try:
        carts_table.put_item(Item=cart)
    except ClientError as exc:
        logger.error("cart_create_failed", correlation_id=correlation_id, error=str(exc))
        return {"status": "error", "message": "unable to create cart",
                "correlation_id": correlation_id}, 500


    # Do not log user_id or other personal information.

    logger.info(
        "cart_created",
        correlation_id=correlation_id,
        cart_id=cart_id,
        items=cart["items"]
    )


    return {

        "status":
            "created",

        "cart_id":
            cart_id,

        "correlation_id":
            correlation_id

    }, 201


@app.route("/cart/<cart_id>/cancel", methods=["POST"])
def cancel_cart_route(cart_id):
    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )

    cancelled, error_message = cancel_cart(
        cart_id,
        correlation_id,
    )

    if not cancelled:
        status_code = 404 if error_message == "cart not found" else 400

        return {
            "status": "error",
            "message": error_message,
            "correlation_id": correlation_id,
        }, status_code

    return {
        "status": "cancelled",
        "cart_id": cart_id,
        "correlation_id": correlation_id,
    }, 200


# =========================================================
# Create Order
# =========================================================

@app.route("/order", methods=["POST"])
def create_order():

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )


    data = request.get_json() or {}


    # -----------------------------------------------------
    # Cart
    # -----------------------------------------------------

    cart_id = data.get(
        "cart_id"
    )


    if not cart_id:

        return {

            "status":
                "error",

            "message":
                "cart_id is required",

            "correlation_id":
                correlation_id

        }, 400


    # -----------------------------------------------------
    # Customer information
    # -----------------------------------------------------

    customer_name = data.get(
        "customer_name"
    )

    customer_email = data.get(
        "customer_email"
    )


    # -----------------------------------------------------
    # Concert information
    # -----------------------------------------------------

    concert = data.get(
        "concert"
    )

    venue = data.get(
        "venue"
    )

    concert_date = data.get(
        "concert_date"
    )

    ticket_location = data.get(
        "ticket_location"
    )


    # -----------------------------------------------------
    # Ticket information
    # -----------------------------------------------------

    amount = data.get(
        "amount",
        0
    )

    items = data.get(
        "items",
        0
    )


    # -----------------------------------------------------
    # Payment information
    #
    # Values are accepted for the demo but NEVER logged.
    # -----------------------------------------------------

    bank_account = data.get(
        "bank_account"
    )

    account_holder = data.get(
        "account_holder"
    )


    # -----------------------------------------------------
    # Validate required information
    # -----------------------------------------------------

    if not customer_name:

        return {

            "status":
                "error",

            "message":
                "customer_name is required",

            "correlation_id":
                correlation_id

        }, 400


    if not customer_email:

        return {

            "status":
                "error",

            "message":
                "customer_email is required",

            "correlation_id":
                correlation_id

        }, 400


    if not concert:

        return {

            "status":
                "error",

            "message":
                "concert is required",

            "correlation_id":
                correlation_id

        }, 400


    if not ticket_location:

        return {

            "status":
                "error",

            "message":
                "ticket_location is required",

            "correlation_id":
                correlation_id

        }, 400


    if not bank_account:

        return {

            "status":
                "error",

            "message":
                "bank_account is required",

            "correlation_id":
                correlation_id

        }, 400


    if not account_holder:

        return {

            "status":
                "error",

            "message":
                "account_holder is required",

            "correlation_id":
                correlation_id

        }, 400


    # -----------------------------------------------------
    # Complete cart
    # -----------------------------------------------------

    try:
        carts_table.update_item(
            Key={"cart_id": cart_id},
            UpdateExpression="SET #status = :completed, updated_at = :now",
            ConditionExpression="attribute_exists(cart_id) AND #status = :active",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":completed": "completed",
                ":active": "active",
                ":now": int(time.time()),
            },
        )

    except ClientError as exc:

        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            existing = carts_table.get_item(Key={"cart_id": cart_id}).get("Item")

            if not existing:
                return {"status": "error", "message": "cart not found",
                        "correlation_id": correlation_id}, 404

            return {"status": "error", "message": f"cart is already {existing['status']}",
                    "correlation_id": correlation_id}, 400

        logger.error("order_cart_complete_failed", correlation_id=correlation_id, cart_id=cart_id, error=str(exc))
        return {"status": "error", "message": "internal error",
                "correlation_id": correlation_id}, 500


        if not cart:

            return {

                "status":
                    "error",

                "message":
                    "cart not found",

                "correlation_id":
                    correlation_id

            }, 404


        if cart["status"] != "active":

            return {

                "status":
                    "error",

                "message":
                    (
                        f"cart is already "
                        f"{cart['status']}"
                    ),

                "correlation_id":
                    correlation_id

            }, 400


        cart["status"] = (
            "completed"
        )


        cart["updated_at"] = (
            time.time()
        )


    # -----------------------------------------------------
    # Generate order ID
    # -----------------------------------------------------

    order_id = (
        f"ord-{uuid.uuid4().hex[:8]}"
    )


    # -----------------------------------------------------
    # Log order
    #
    # IMPORTANT:
    #
    # Personal information is intentionally NOT logged:
    #
    # - customer_name
    # - customer_email
    # - bank_account
    # - account_holder
    #
    # Only non-sensitive operational/business information
    # is included.
    # -----------------------------------------------------

    logger.info(
        "order_created",

        correlation_id=
            correlation_id,

        order_id=
            order_id,

        cart_id=
            cart_id,

        concert=
            concert,

        venue=
            venue,

        concert_date=
            concert_date,

        ticket_location=
            ticket_location,

        amount=
            amount,

        items=
            items
    )


    # -----------------------------------------------------
    # Return only information required by the UI.
    # Personal/payment information is not returned.
    # -----------------------------------------------------

    record_business_metrics(
        "order_completed",
        band=concert,
        zone=ticket_location,
        tickets=items,
    )

    return {

        "status":
            "created",

        "order_id":
            order_id,

        "cart_id":
            cart_id,

        "correlation_id":
            correlation_id

    }, 201


# =========================================================
# Cart Abandonment Metric
#
# Kept for monitoring.
# Removed from the UI.
# =========================================================
def _count_carts_by_status(status):
    count = 0
    query_kwargs = {
        "IndexName": "status-updated_at-index",
        "KeyConditionExpression": "#status = :status",
        "ExpressionAttributeNames": {"#status": "status"},
        "ExpressionAttributeValues": {":status": status},
        "Select": "COUNT",
    }

    response = carts_table.query(**query_kwargs)
    count += response["Count"]

    while "LastEvaluatedKey" in response:
        response = carts_table.query(
            **query_kwargs,
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        count += response["Count"]

    return count

@app.route("/metrics/cart-abandonment")
def cart_abandonment_metric():

    try:
        abandoned_carts = _count_carts_by_status("abandoned")
        completed_carts = _count_carts_by_status("completed")
        active_carts = _count_carts_by_status("active")
    except ClientError as exc:
        logger.error("cart_abandonment_metric_failed", error=str(exc))
        return {"status": "error", "message": "unable to compute metric"}, 500

    total_carts = abandoned_carts + completed_carts + active_carts
    completed_or_cancelled = completed_carts + abandoned_carts

    if completed_or_cancelled == 0:
        abandonment_rate = 0
    else:
        abandonment_rate = (abandoned_carts / completed_or_cancelled) * 100

    logger.info(
        "cart_abandonment_metric_requested",
        metric_name="CartAbandonmentRate",
        total_carts=total_carts,
        abandoned_carts=abandoned_carts,
        completed_carts=completed_carts,
        active_carts=active_carts,
        abandonment_rate=round(abandonment_rate, 2)
    )

    return {
        "metric": "CartAbandonmentRate",
        "abandoned_carts": abandoned_carts,
        "completed_carts": completed_carts,
        "active_carts": active_carts,
        "total_carts": total_carts,
        "abandonment_rate_percent": round(abandonment_rate, 2)
    }


# =========================================================
# Simulated Error
#
# Kept for monitoring/testing.
# Removed from the UI.
# =========================================================

@app.route("/error")
def error():

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )


    logger.error(
        "request_failed",
        correlation_id=correlation_id,
        path="/error",
        error="simulated failure"
    )


    return {

        "status":
            "error",

        "correlation_id":
            correlation_id

    }, 500


# =========================================================
# Simulate Slow Requests
#
# Kept for latency/observability testing.
# Removed from the UI.
# =========================================================

@app.route("/slow")
def slow():

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid.uuid4())
    )


    try:

        delay = float(
            request.args.get(
                "delay",
                "1"
            )
        )


    except ValueError:

        return {

            "status":
                "error",

            "message":
                "delay must be a number",

            "correlation_id":
                correlation_id

        }, 400


    delay = max(
        0,
        min(
            delay,
            30
        )
    )


    logger.info(
        "slow_request",
        correlation_id=correlation_id,
        delay=delay
    )


    time.sleep(
        delay
    )


    return {

        "status":
            "ok",

        "delay":
            delay,

        "correlation_id":
            correlation_id

    }


# =========================================================
# Start Application
# =========================================================

if __name__ == "__main__":

    logger.info(
        "application_started",

        port=5000,

        cart_monitoring_interval=
            CART_MONITORING_INTERVAL,

        cart_abandonment_timeout=
            CART_ABANDONMENT_TIMEOUT
    )


    app.run(
        host="0.0.0.0",
        port=5000
    )

