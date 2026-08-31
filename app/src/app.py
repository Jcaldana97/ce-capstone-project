import structlog
from flask import Flask, request, g, render_template
import uuid
import time
import threading
import os
import socket
import urllib.request


# =========================================================
# Configuration
# =========================================================

CART_ABANDONMENT_TIMEOUT = 120

CART_MONITORING_INTERVAL = 30


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


# =========================================================
# In-memory cart storage
#
# Demo only.
#
# For multiple EC2 instances this should eventually be
# replaced with DynamoDB, Redis, or another shared datastore.
# =========================================================

carts = {}

cart_lock = threading.Lock()


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
# Cart Monitoring
# =========================================================

def monitor_carts():

    while True:

        try:

            now = time.time()

            newly_abandoned = 0


            with cart_lock:

                for cart in carts.values():

                    if (
                        cart["status"] == "active"
                        and
                        now - cart["updated_at"]
                        >= CART_ABANDONMENT_TIMEOUT
                    ):

                        cart["status"] = "abandoned"

                        newly_abandoned += 1

                        logger.info(
                            "cart_abandoned",
                            cart_id=cart["cart_id"],
                            user_id=cart["user_id"]
                        )


                total_carts = len(carts)


                abandoned_carts = sum(
                    1
                    for cart in carts.values()
                    if cart["status"] == "abandoned"
                )


                completed_carts = sum(
                    1
                    for cart in carts.values()
                    if cart["status"] == "completed"
                )


                active_carts = sum(
                    1
                    for cart in carts.values()
                    if cart["status"] == "active"
                )


            if total_carts == 0:

                abandonment_rate = 0

            else:

                abandonment_rate = (
                    abandoned_carts /
                    total_carts
                ) * 100


            logger.info(
                "cart_abandonment_metric",
                metric_name="CartAbandonmentRate",
                total_carts=total_carts,
                newly_abandoned=newly_abandoned,
                abandoned_carts=abandoned_carts,
                completed_carts=completed_carts,
                active_carts=active_carts,
                abandonment_rate=round(
                    abandonment_rate,
                    2
                )
            )


        except Exception as exc:

            logger.error(
                "cart_monitoring_failed",
                error=str(exc)
            )


        time.sleep(
            CART_MONITORING_INTERVAL
        )


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


    with cart_lock:

        carts[cart_id] = cart


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

    with cart_lock:

        cart = carts.get(
            cart_id
        )


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

@app.route("/metrics/cart-abandonment")
def cart_abandonment_metric():

    with cart_lock:

        total_carts = len(carts)


        abandoned_carts = sum(
            1
            for cart in carts.values()
            if cart["status"] == "abandoned"
        )


        completed_carts = sum(
            1
            for cart in carts.values()
            if cart["status"] == "completed"
        )


        active_carts = sum(
            1
            for cart in carts.values()
            if cart["status"] == "active"
        )


    if total_carts == 0:

        abandonment_rate = 0

    else:

        abandonment_rate = (
            abandoned_carts /
            total_carts
        ) * 100


    logger.info(
        "cart_abandonment_metric_requested",
        metric_name="CartAbandonmentRate",
        total_carts=total_carts,
        abandoned_carts=abandoned_carts,
        completed_carts=completed_carts,
        active_carts=active_carts,
        abandonment_rate=round(
            abandonment_rate,
            2
        )
    )


    return {

        "metric":
            "CartAbandonmentRate",

        "abandoned_carts":
            abandoned_carts,

        "completed_carts":
            completed_carts,

        "active_carts":
            active_carts,

        "total_carts":
            total_carts,

        "abandonment_rate_percent":
            round(
                abandonment_rate,
                2
            )

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

