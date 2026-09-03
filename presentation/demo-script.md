# Demo script

## First Demo: Test High Error Rate Alarm

Run the following commands: 

```bash
for j in {1..3}
  for i in {1..50}; do
    curl http://$ALB_DNS/error &
  done
  sleep 30
done
```

## Second Demo: Test High CPU Usage Alarm + Autoscaling group

In order to inject the failure:

- Open 3 command windows to have access to the three instances running. 

```bash
aws ssm start-session --target 
```

- Run the following command on each instance to stress the CPU. 

```bash 
timeout 720 bash -c 'for i in $(seq 1 $(nproc)); do while :; do :; done & done; wait'
```

- After some time, due to the stress on the current instances, the autoscaling group will launch new instances (between 1 to 3)

## Third Demo: Test High Unhealthy Targets Alert

- Access to at least 2 instances: 

```bash
aws ssm start-session --target 
```

- Run the following command 

```bash 
sudo systemctl stop flask-app
```

## Fourth Demo: Bussiness metrics 

1. Open the following website in a browser:

```bash
http://capstone-project-alb-931963269.us-east-1.elb.amazonaws.com/ui
```

2. Select the desired band. 

3. Add personal information

4. Complete the order by clicking "Complete order"

5. A message box should display "Order completed" and some information such as the correlation and cart id. Please save this information. 

6. Click on another band. 

7. After selecting a band, a timer will start counting down from 60 seconds. 

8. Let the timer reaches 0 (for cart abandonement rate testing)
