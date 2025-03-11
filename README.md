TransMail-Station
===

[简体中文](./README.zh-CN.md)

# Introduction

TransMail Station is an HTTP-based email management service designed to help business logic send and manage emails via HTTP requests, thereby decoupling the email-sending functionality from core business logic.

* Features:
  * Multi-recipient email sending (load balancing)
  * Designated sending services
  * Scheduled sending
  * RESTful API
  * Docker Compose deployment
* Use Cases:
  * As a microservice for centralized email dispatching
  * Suitable for projects that need to separate email-sending functionality from core business logic.
  * Provides simple and easy-to-use interfaces to reduce development complexity and accelerate business development.

# Quick Start
## 1. Clone the project and modify the configuration
```shell
# Clone the project
git clone https://github.com/qqAys/TransMail-Station.git
cd TransMail-Station
# Modify the configuration
mv ./config/config.example.yml ./config/config.yml
vim ./config/config.yml
```
For detailed configuration instructions, see [config.example.yml](./config/config.example.yml).

## 2. Start the container using `docker-compose.yml`
```shell
docker-compose up -d
```

## 3. Use the API
Visit [TransMail-Station - Swagger UI](http://localhost:8100/docs) to view the API documentation and integrate it into your business code.

# License
This project is licensed under the MIT License.
