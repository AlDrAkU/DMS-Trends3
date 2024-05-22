<!-- Docker -->
## Compose File

All the services in the project are defined in the docker-compose.yml
To build or start the services, go to the directory of the compose file and execute one of the following commands.

To build all the docker images of the project:
```sh
docker-compose build
```
To start all the services of the project:
```sh
docker-compose build
```
<!-- RabbitMQ Docker -->
## RabbitMQ - Docker

To acces the RabbitMQ management interface, you need to navigate to it in your web browser.
You can use following URL. The exposed port is configured in the compose file.

http://localhost:15672

The default username and password are configured in the compose file.

The RabbitMQ management interface allows you to see the messages from the DMS.

Configuration of the queues are done in the applications itself.

<!-- Postgres SQL Docker -->
## PostgresSQL - Docker

The repository service will store the paths of the validate documents along with some other metrics.

To view or edit the database, you can use psql. It enables you to interact with the PostgresSQL server.
```sh
docker exec -it <container_id> psql -U postgres -d DMS
```

<!-- Repository Service -->
## Repository Service

The app.py generates a swagger page where the api's can be tested. When running the application it can be accessed with this URL:
http://127.0.0.1:5006/apidocs/

<!-- Viewer Service -->
## Viewer Service

The app.py generates a swagger page where the api's can be tested. When running the application it can be accessed with this URL:
http://127.0.0.1:5005/apidocs/

<!-- DMS Viewer -->
## DMS Viewer
The viewer service also includes a small frontend to view the documents. The frontend can be accessed with this URL:
http://127.0.0.1:5005/

