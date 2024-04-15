# Use the official RabbitMQ image as the base image
FROM rabbitmq:latest

# Expose the ports required for RabbitMQ
EXPOSE 5672 15672

# Add any custom configuration files if needed
# COPY rabbitmq.config /etc/rabbitmq/

# Add any additional setup or configuration commands here
# For example, enabling the RabbitMQ management plugin
RUN rabbitmq-plugins enable rabbitmq_management
