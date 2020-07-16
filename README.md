# Clustinator

Clustinator is an incremental clustering service for [ContinuITy](https://github.com/ContinuITy-Project/ContinuITy), which is the open-source implementation of a research project on “Automated Performance Testing in Continuous Software Engineering”, launched by [Novatec Consulting GmbH](https://www.novatec-gmbh.de/) and the [University of Stuttgart](https://www.uni-stuttgart.de/) ([Reliable Software Systems Group](https://www.iste.uni-stuttgart.de/rss/)). ContinuITy started in September 2017 with a duration of 2.5 years. It is funded by the [German Federal Ministry of Education and Research (BMBF)](https://www.bmbf.de/). For details about the research project, please refer to our [Web site](https://continuity-project.github.io/).

## Functionality

Clustinator integrates with the application architecture of [ContinuITy](https://github.com/ContinuITy-Project/ContinuITy). Being triggered via [RabbitMQ](https://www.rabbitmq.com/) by the [Cobra service](https://github.com/ContinuITy-Project/ContinuITy/tree/master/continuity.service.cobra), it retrieves sessions from an [Elasticsearch](https://www.elastic.co/), clusters them into user groups of similar behavior, stores the results into the Elasticsearch, and reports back to the remaining ContinuITy services. The user behavior representation relates to the [WESSBAS-DSL](https://github.com/Wessbas/wessbas.dsl).

## Running Clustinator

### Run via Docker

We provide Clustinator as a [Docker image](https://hub.docker.com/r/continuityproject/clustinator), which can be easily executed as follows:

```
docker run continuityproject/clustinator
```

The following configuration options can be added as environment variable (using the `-e` flag). The default properties fit the default ContinuITy Docker setup.

* `RABBITMQ`: Host name of the RabbitMQ server. Defaults to *rabbitmq*.
* `ELASTIC`: Host name of Elasticsearch. Defaults to *cobra-db*.
* `RABBITMQ_TIMEOUT`: The timeout in seconds after which the RabbitMQ connection is treated to be dead. Defaults to *60*.
* `ELASTIC_TIMEOUT`: The timeout in seconds to wait for an Elasticsearch request. Defaults to *10*.
* `SESSIONS_BUFFER`: A file path to a session matrix buffer. None (the default) means not buffering the matrices. The path is *inside* the Docker container and can be mapped to a local folder as a volume.
* `FAST_TEST`: Set to true to do a fast test run without think time calculation. DO NOT USE IN PRODUCTION! Defaults to *false*.

### Build and Run Locally

Clustinator can also be executed locally, e.g., when developing the service. *We recommend using Python 3.6*.

Check out this Git repository and install the required packages:

```
pip install -r requirements.txt
```

Then, go to the folder `clustinator` and run the service using the following command:

```
python receiver.py [-h] [--rabbitmq [RABBITMQ]]
                   [--rabbitmq-port [RABBITMQ_PORT]] [--elastic [ELASTIC]]
                   [--timeout [TIMEOUT]] [--elastic-timeout [ELASTIC_TIMEOUT]]
                   [--sessions-buffer [SESSIONS_BUFFER]] [--fast-test]
```

Optional arguments are the following:

* `-h`, `--help`: Show a help message and exit.
* `--rabbitmq [RABBITMQ]`: The host name or IP of the RabbitMQ server. Defaults to *localhost*.
* `--rabbitmq-port [RABBITMQ_PORT]`: The port number of the RabbitMQ server. Defaults to *5672*.
* `--elastic [ELASTIC]`: The host name or IP of the elasticsearch server. Defaults to *localhost*.
* `--timeout [TIMEOUT]`: The timeout in seconds after which the RabbitMQ connection is treated to be dead. Defaults to *None*, which accepts the server's proposal.
* `--elastic-timeout [ELASTIC_TIMEOUT]`: The timeout in seconds to wait for an Elasticsearch request. Defaults to *10*.
* `--sessions-buffer [SESSIONS_BUFFER]`: A file path to a session matrix buffer. *None* (the default) means not buffering the matrices.
* `--fast-test`: Set to true to do a fast test run without think time calculation. DO NOT USE IN PRODUCTION!

## Scientific Publications

Clustinator implements or is based on the work of several scientific publications, which we list in the following. Here, we only consider publications that directly influenced the implementation; further publications of the ContinuITy project are available on the [project web site](https://continuity-project.github.io/publications.html).

* Henning Schulz, Tobias Angerstein, and André van Hoorn: *Towards Automating Representative Load Testing in Continuous Software Engineering* ([full paper](https://dl.acm.org/citation.cfm?id=3186288)), Companion of the International Conference on Performance Engineering (ICPE) 2018, Berlin, Germany 
* Christian Vögele, André van Hoorn, Eike Schulz, Wilhelm Hasselbring, and Helmut Krcmar: *WESSBAS: extraction of probabilistic workload specifications for load testing and performance prediction - a model-driven approach for session-based application systems*, Software and Systems Modeling 17(2): 443-477 (2018)

## License

This project is licensed under Apache v2 - see the [LICENSE](LICENSE) file for details.
