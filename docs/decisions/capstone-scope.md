# Capstone Project: Concert Ticket Service
 
## Overview
The application consists of a python script that defines the following endpoints:
- **/health**: indicates the status of the server
- **/error**: simulates error responses
- **/ui**: displays the user interface of the server
- **/instance-info**: shows the relevant information about the instance running (ID and AZ)
- **/cart**: creates a cart for the ticket purchase
- **/cart/<cart_id>/cancel**: cancels the cart after a timeout
- **/order**: completes the order with cart_id
- **/metrics/cart-abandonment**: calculates the abandonment rate of the server
- **/slow**: simulates slow responses

The general goal of the website is to let the customer select a concert available for his favourite band, ask for personal information and bank details to complete the purchase, give a brief summary of the order and complete the order. 
 
## Architecture
- Frontend: HTML
- Backend: Python Flask app and Gunicorn
- Database: DynamoDB
 
## User Stories
1. As a user, I can register an account
2. As a user, I can log in with email/password
3. As a user, I can view my dashboard
4. As a user, I can view the alerts and receive notifications
 
## Security Requirements
- Authentication with MFA
- Data encrypted at rest and in transit
- Least-privilege IAM roles