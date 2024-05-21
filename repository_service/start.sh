#!/bin/bash

# Wait for RabbitMQ server to be ready
until python -c 'import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(("rabbitmq", 5672))' &> /dev/null; do
    echo "$(date) - waiting for RabbitMQ server at 'rabbitmq:5672'..."
    sleep 1
done

# Now we know the RabbitMQ server is ready, we can start the application
python app.py  # Replace this with your actual command
