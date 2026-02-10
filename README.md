# C1_llm_email_replier

The LLM Email Replier (C1) is a processing component that demonstrates 
the use of Large Language Models (LLMs) to automate communication. It receives 
incoming email data from other components, processes the text using a 
pre-trained model, and generates a refined reply. Users can dynamically 
customize its behavior by adjusting generation parameters (like creativity 
and length) and defining a specific "persona" through a system prompt.


## Summary

- **Type**: [C1](https://valawai.github.io/docs/components/C1/)
- **Name**: LLM e-mail replier
- **Documentation**: [https://valawai.github.io/docs/components/C1/llm_email_replier](https://valawai.github.io/docs/components/C1/llm_email_replier)
- **Versions**:
  - **Stable version**: [1.2.0 (February 10, 2026)](https://github.com/VALAWAI/C1_llm_email_replier/tree/1.2.0)
  - **API**: [1.0.0 (March 16, 2024)](https://raw.githubusercontent.com/VALAWAI/C1_llm_email_replier/ASYNCAPI_1.0.0/asyncapi.yml)
  - **Required MOV API**: [1.2.0 (March 9, 2024)](https://raw.githubusercontent.com/valawai/MOV/ASYNCAPI_1.2.0/asyncapi.yml)
- **Developed By**: [IIIA-CSIC](https://www.iiia.csic.es)
- **License**: [GPL v3](LICENSE)
- **Technology Readiness Level (TLR)**: [3](https://valawai.github.io/docs/components/C1/llm_email_replier/tlr)


## Usage

The LLM Email Replier (C1) is a processing component that leverages 
Large Language Models to automate email responses within the VALAWAI 
framework. It acts as a "brain" in the processing pipeline by transforming 
incoming message data into refined communication products.


## Deployment

The **C1 LLM E-Mail Replier** is designed to run as a Docker container, working within 
the [Master Of VALAWAI (MOV)](https://valawai.github.io/docs/architecture/implementations/mov) ecosystem. 
For a complete guide, including advanced setups, refer to 
the [component's full deployment documentation](https://valawai.github.io/docs/components/C1/llm_email_replier/deploy).

Here's how to quickly get it running:

1. ### Build the Docker Image

    First, you need to build the Docker image. Go to the project's root directory and run:

    ```bash
    ./buildDockerImages.sh -t latest
    ```

    This creates the `valawai/c1_llm_email_replier:latest` Docker image, which is referenced in the `docker-compose.yml` file.

2. ### Start the Component

    You have two main ways to start the component:

    A. **With MOV and Mail Catcher (for testing):**
    To run the C1 E-mail replier with the MOV, use:

    ```bash
    COMPOSE_PROFILES=all docker compose up -d
    ```

    Once started, you can access:

    - **MOV:** [http://localhost:8081](http://localhost:8081)
    - **RabbitMQ UI:** [http://localhost:8082](http://localhost:8082) (credentials: `mov:password`)
    - **Mongo DB:** `localhost:27017` (credentials: `mov:password`)

    B. **As a Standalone Component (connecting to an existing MOV/RabbitMQ):**
    If you already have MOV running or want to connect to a remote RabbitMQ, you'll need a [`.env` file](https://docs.docker.com/compose/environment-variables/env-file/) with connection details. Create a `.env` file in the same directory as your `docker-compose.yml` like this:

    ```properties
    MOV_MQ_HOST=host.docker.internal
    MOV_MQ_USERNAME=mov
    MOV_MQ_PASSWORD=password
    ```

    Find full details on these and other variables in the [component's dedicated deployment documentation](https://valawai.github.io/docs/components/C1/llm_email_replier/deploy).
    Once your `.env` file is configured, start only the email actuator and mail catcher (without MOV) using:

    ```bash
    COMPOSE_PROFILES=component docker compose up -d
    ```

## Development environment

To ensure a consistent and isolated development experience, this component is configured
to use Docker. This approach creates a self-contained environment with all the necessary
software and tools for building and testing, minimizing conflicts with your local system
and ensuring reproducible results.

You can launch the development environment by running this script:

```bash
./startDevelopmentEnvironment.sh
```

Once the environment starts, you'll find yourself in a bash shell, ready to interact with
the Quarkus development environment. You'll also have access to the following integrated tools:

- **Master of VALAWAI**: The central component managing topology connections between services.
 Its web interface is accessible at [http://localhost:8081](http://localhost:8081).
- **RabbitMQ** The message broker for inter-component communication. The management web interface
 is at [http://localhost:8082](http://localhost:8082), with credentials `mov**:**password`.
- **MongoDB**: The database used by the MOV, named `movDB`, with user credentials `mov:password`.
- **Mongo express**: A web interface for interacting with MongoDB, available at
 [http://localhost:8084](http://localhost:8084), also with credentials `mov**:**password`.

Within this console, you can use the next commands:

* **run:** Starts the C1 E-Mail replier component.
* **testAll:** Runs all unit tests for the codebase.
* **test test/test_something.py:** Runs the unit tests defined in
 the file `test_something.py`.
* **test test/test_something.py::TestClassName::test_do_something:** Runs 
a specific unit test named `test_do_something` defined within the class `TestClassName` 
in the file `test_something.py`.
* **coverage:** Runs all unit tests and generates a coverage report.
* **fmt:** Runs a static code analyzer to check for formatting and style issues.

To exit the development environment, simply type `exit` in the bash shell or run the following script:

```bash
./stopDevelopmentEnvironment.sh
```

In either case, the development environment will gracefully shut down, including all activated services like MOV, RabbitMQ, MongoDB, and Mongo Express.

  
## Development

You can start the development environment with the script:

```shell script
./startDevelopmentEnvironment.sh
```

After that, you have a bash shell where you can interact with the Python code. You can use the next command
to so some common action.

* **run** to start the component.
* **testAll** to run all the unit tests
* **test test/test_something.py** to run the tests defined on the file **test_something.py**
* **test test/test_something.py -k test_do_something** to run the test named **test_do_something** defined on the file **test_something.py**

Also, this starts the tools:

 * **RabbitMQ** is the server that manages the message brokers.
 The management web interface can be opened at **http://localhost:8081** with the credential
 **mov**:**password**.
 * **MongoDB** is the database used by the MOV. The database is named **movDB** and the user credentials **mov:password**.
 The management web interface can be opened at **http://localhost:8081** with the credential
 **mov**:**password**.
 * **Mongo express** is the web interface to interact with the MongoDB. The web interface
 can be opened at **http://localhost:8082**.
 * **Master Of VALAWAI (MOV)** the web interface to interact with the Master Of VALWAI(MOV). The web interface
 can be opened at **http://localhost:8083**.


## Helpful Links

Here's a collection of useful links related to this component and the VALAWAI ecosystem:

- **C1 LLM e-mail replier Documentation**: [https://valawai.github.io/docs/components/C1/llm_email_replier](https://valawai.github.io/docs/components/C1/llm_email_replier)
- **Master Of VALAWAI (MOV)**: [https://valawai.github.io/docs/architecture/implementations/mov/](https://valawai.github.io/docs/architecture/implementations/mov/)
- **VALAWAI Main Documentation**: [https://valawai.github.io/docs/](https://valawai.github.io/docs/)
- **VALAWAI on GitHub**: [https://github.com/VALAWAI](https://github.com/VALAWAI)
- **VALAWAI Official Website**: [https://valawai.eu/](https://valawai.eu/)
- **VALAWAI on X (formerly Twitter)**: [https://x.com/ValawaiEU](https://x.com/ValawaiEU)
