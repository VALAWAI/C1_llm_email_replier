# C1_llm_email_replier

The C1 LLM e-mail replier component receive e-mails from C0 components, generate a reply
using a large language model (LLM), and send it back to other C0 components to publish it.
You can read more about this service and the payload of the message on
the [aysncapi](asyncapi.yaml) or on the [component documentation](https://valawai.github.io/docs/components/C1/llm_email_replier).

## Summary

 - Type: C1
 - Name: LLM e-mail replier
 - API: [1.0.0 (August 16, 2024)](https://raw.githubusercontent.com/VALAWAI/C1_llm_email_replier/ASYNCAPI_1.0.0/asyncapi.yml)
 - VALAWAI API: [1.2.0 (March 9, 2024)](https://raw.githubusercontent.com/valawai/MOV/ASYNCAPI_1.2.0/asyncapi.yml)
 - Developed By: [IIIA-CSIC](https://www.iiia.csic.es)
 - License: [GPL 3](LICENSE)


## Generate Docker image

The easy way to create the docker image of this component is to execute
the next script.
 
 ```
./buildDockerImages.sh
```

At the end you must have the docker image **valawai/c1_llm_email_replier:Z.Y.Z**
where **X.Y.Z** will be the version of the component. If you want to have
the image with another tag, for example **latest**, you must call the script
with this tag as a parameter, for example:

```
./buildDockerImages.sh latest
```

And you will obtain the container **valawai/c1_llm_email_replier:latest**.

The most useful environment variables on the docker image are:

 - **RABBITMQ_HOST** is the host where the RabbitMQ is available.
 The default value is **mov-mq**.
 - **RABBITMQ_PORT** defines the port of the RabbitMQ.
 The default value is **5672**.
 - **RABBITMQ_USERNAME** contains the user's name that can access the RabbitMQ.
 The default value is **mov**.
 - **RABBITMQ_PASSWORD** is the password used to authenticate the user who can access the RabbitMQ.
 The default value is **password**.
 - **RABBITMQ_MAX_RETRIES** 100
 - **RABBITMQ_RETRY_SLEEP** 3
 - **REPLY_MAX_NEW_TOKENS** The number maximum of tokens to generate. The default value is **256**.
 - **REPLY_TEMPERATURE** The value used to modulate the next token probabilities. The default value is **0.7**.
 - **REPLY_TOP_K** The number of highest probability tokens to consider for generating the output.
 The default value is **50**.
 - **REPLY_TOP_P** A probability threshold for generating the output, using nucleus filtering.
 The default value is **0.95**.
 - **REPLY_SYSTEM_PROMPT** The prompt to use as system. It is used to define how the reply must be done. 
 The default value is **You are a polite chatbot who always try to provide solutions to the customers problems**.
 - **LOG_CONSOLE_LEVEL** defines the level of the log messages to be show in the console.
 The possible values are: CRITICAL, FATAL, ERROR, WARN, WARNING, INFO or DEBUG. The default value is **INFO**.
 - **LOG_FILE_LEVEL** defines the level of the log messages to be stored in the log file.
 The possible values are: CRITICAL, FATAL, ERROR, WARN, WARNING, INFO or DEBUG. The default value is **DEBUG**.
 - **LOG_FILE_MAX_BYTES** defines the maximum number of bytes that the log file can have before rolling.
  The default value is **1000000**.
 - **LOG_FILE_BACKUP_COUNT** defines the maximum number of rolling files to mantain.
  The default value is **5**.


## Deploy

On the file [docker-compose.yml](docker-compose.yml), you can see how the docker image
of this component can be deployed on a valawai environment. On this file are defined
the profiles **mov** and **mail**. The first one is to launch
the [Master Of Valawai (MOV)](https://github.com/VALAWAI/MOV). You can use the next
command to start this component with the MOV.

```
COMPOSE_PROFILES=mov docker compose up -d
```

After that, if you open a browser and go to [http://localhost:8080](http://localhost:8080)
you can view the MOV user interface. Also, you can access the RabbitMQ user interface
at [http://localhost:8081](http://localhost:8081) with the credentials **mov:password**.

The docker compose defines some variables that can be modified by creating a file named
[**.env**](https://docs.docker.com/compose/environment-variables/env-file/) where 
you write the name of the variable plus equals plus the value.  As you can see in
the next example.

```
MQ_HOST=rabbitmq.valawai.eu
MQ_USERNAME=c1_llm_email_replier
MQ_PASSWORD=lkjagb_ro82t¿134
```

The defined variables are:


 - **C1_LLM_EMAIL_REPLIER_TAG** is the tag of the C1 llm e-mail replier docker image to use.
 The default value is **latest**.
 - **MQ_HOST** is the hostname of the message queue broker that is available.
 The default value is **mq**.
 - **MQ_PORT** is the port of the message queue broker is available.
 The default value is **5672**.
 - **MQ_UI_PORT** is the port of the message queue broker user interface is available.
 The default value is **8081**.
 - **MQ_USER** is the name of the user that can access the message queue broker.
 The default value is **mov**.
 - **MQ_PASSWORD** is the password used to authenticate the user who can access the message queue broker.
 The default value is **password**.
 - **RABBITMQ_TAG** is the tag of the RabbitMQ docker image to use.
 The default value is **management**.
 - **MONGODB_TAG** is the tag of the MongoDB docker image to use.
 The default value is **latest**.
 - **MONGO_PORT** is the port where MongoDB is available.
 The default value is **27017**.
 - **MONGO_ROOT_USER** is the name of the root user for the MongoDB.
 The default value is **root**.
 - **MONGO_ROOT_PASSWORD** is the password of the root user for the MongoDB.
 The default value is **password**.
 - **MONGO_LOCAL_DATA** is the local directory where the MongoDB will be stored.
 The default value is **~/mongo_data/movDB**.
 - **DB_NAME** is the name of the database used by the MOV.
 The default value is **movDB**.
 - **DB_USER_NAME** is the name of the user used by the MOV to access the database.
 The default value is **mov**.
 - **DB_USER_PASSWORD** is the password of the user used by the MOV to access the database.
 The default value is **password**.
 - **MOV_TAG** is the tag of the MOV docker image to use.
 The default value is **latest**.
 - **MOV_UI_PORT** is the port where the MOV user interface is available.
 The default value is **8080**.
 - **REPLY_MAX_NEW_TOKENS** The number maximum of tokens to generate. The default value is **256**.
 - **REPLY_TEMPERATURE** The value used to modulate the next token probabilities. The default value is **0.7**.
 - **REPLY_TOP_K** The number of highest probability tokens to consider for generating the output.
 The default value is **50**.
 - **REPLY_TOP_P** A probability threshold for generating the output, using nucleus filtering.
 The default value is **0.95**.
 - **REPLY_SYSTEM_PROMPT** The prompt to use as system. It is used to define how the reply must be done. 
 The default value is **You are a polite chatbot who always try to provide solutions to the customers problems**.
 - **LOG_LEVEL** defines the level of the log messages to be show in the console.
 The possible values are: CRITICAL, FATAL, ERROR, WARN, WARNING, INFO or DEBUG. The default value is **INFO**.


The database is only created the first time where script is called. So, if you modify
any of the database parameters you must create again the database. For this, you must
remove the directory defined by the parameter **MONGO_LOCAL_DATA** and start again
the **docker compose**.

You can stop all the started containers with the command:

```
COMPOSE_PROFILES=mov docker compose down
```
  
## Development

You can start the development environment with the script:

```shell script
./startDevelopmentEnvironment.sh
```

TO DO

* **testAll** to runing all all the tests

Also, this starts the tools:

 * **RabbitMQ**  the server to manage the messages to interchange with the components.
 The management web interface can be opened at **http://localhost:8081** with the credential
 **mov**:**password**.
 * **MongoDB**  the database to store the data used by the MOV. The database is named as **movDB** and the user credentials **mov:password**.
 The management web interface can be opened at **http://localhost:8081** with the credential
 **mov**:**password**.
 * **Mongo express**  the web interface to interact with the MongoDB. The web interface
  can be opened at **http://localhost:8082**.
 * **Master Of VALAWAI (MOV)**  the web interface to interact with the Master Of VALWAI(MOV). The web interface
  can be opened at **http://localhost:8083**.


## Links

 - [C1 LLM e-mail replier documentation](https://valawai.github.io/docs/components/C1/llm_email_replier)
 - [Master Of VALAWAI tutorial](https://valawai.github.io/docs/tutorials/mov)
 - [VALWAI documentation](https://valawai.github.io/docs/)
 - [VALAWAI project web site](https://valawai.eu/)
 - [Twitter](https://twitter.com/ValawaiEU)
 - [GitHub](https://github.com/VALAWAI)