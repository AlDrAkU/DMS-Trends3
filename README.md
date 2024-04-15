<!-- RabbitMQ -->
## RabbitMQ
<!-- RabbitMQ Docker -->
### RabbitMQ - Docker

Build Image:
```sh
docker build -t rabbitmq .
```
Run Container:
```sh
docker run -d --name rabbitmq_container -p 5672:5672 -p 15672:15672 rabbitmq
```
<!-- RabbitMQ Configuration -->
### RabbitMQ - Configuration
#### Overview Tab
Export definitions saves the changes made to a json file.

Import definitions imports a configuration from a definitions json file.