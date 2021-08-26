# Developer Guide

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Docker](#docker)

## Getting Started

So you want to contribute code to the OpenSearch k-NN Performance Tool?
Excellent! Or you just want to learn more about the tool? Either way, we're glad
you're here. Here's what you should know.

## Development Environment

### Python

Python 3.7 or above is required. Then install the necessary requirements:

```
pip install -r requirements.txt
```

### Linting

We use [`pylint`](https://www.pylint.org/) for static analysis and other checks
on `.py` files. After installing `pylint`, you can check your code by running:

```
pylint opensearch-knn-perf-tool.py okpt/**/*.py
```

The full set of rules and settings can be found [here](/.pylintrc).

### Formatting

We use [`yapf`](https://github.com/google/yapf) and the `google` style to format
our code. After installing `yapf`, you can format your code by running:

```
yapf --style google opensearch-knn-perf-tool.py okpt/**/*.py
```

The full set of formatting rules can be found [here](/.style.yapf).

### Docker

We use Docker to run the tests which you can download
[here](https://www.docker.com/get-started). Most versions of Docker already come
with Docker Compose, but if yours doesn't, make sure to
[install it](https://docs.docker.com/compose/install/).

## Project Structure

The official tool name is the OpenSearch k-NN Performance Tool, but the `python`
module name is `okpt`. The tool code is all under the `okpt/` directory but we
provide an entrypoint script to the module as `knn-perf-tool.py`.

All tool related configuration is in the `config/` directory and separated by
k-NN service. All of the `YAML` files provided are just default values and
should be modified/replaced if running any extensive tests.

All Docker related configuration is in the `docker/` directory and separated by
k-NN service. All of the `YAML`, `.env` files provided are just default values
and should be modified/replaced if running any extensive tests.

Datasets for tests are in the `dataset/` directory.

## Configuration

The tool configuration is intended to be simple and easy to use but also highly
extensible as well. Each k-NN service has different configuration requirements
and as such, the tool needs a robust parsing and validation system for config
files. There are two main configuration components: **tool** configuration and
**service** configuration.

The **tool** configuration includes things such as the `test_name`,
`knn_service`, `test_parameters`, and other service-independent settings.

The **service** configuration contains settings relevant to a particular k-NN
service, so for OpenSearch, this could include things like `max_num_segments` or
`bulk_size` while for NMSLIB, this could be `post` or `ef_construction` (this is
actually in OpenSearch as well, but since OpenSearch uses other services under
the hood, OpenSearch settings are usually a superset of a service's settings).

The tool and service configuration settings are specified in
[YAML](https://yaml.org/) for readability and ease of use. The process of
parsing configuration files looks like:

<div align="center">
  <img src="images/config-parsing-process.png" alt="config process" />
</div>

### Configuration Tree

Despite the tool and service configs being logically separate, the entire
configuration object is actually nested. Only the tool config is passed to the
performance tool, so the service config is specified in the tool config. Service
configs may be further nested as well, such as OpenSearch, whose service config
specifies a `JSON` file which eventually needs to be parsed into a dictionary.

The configuration hierarchy ends up in tree-like structure:

<div align="center">
  <img src="images/config-hierarchy.png" alt="config hierarchy" />
</div>

### Configuration Parsing

Since parsing the configuration is similar to parsing a tree, it isn't such a
straightforward process. We take a top-down approach to parsing. If using
OpenSearch as the k-NN service, we would first convert and validate the tool
config. If that succeeds, we then convert and validate the service config
(specified in the tool config). This process continues until we've reached the
bottom of the configuration tree.

We have provided a base `Parser` interface that performs the general conversion
and validation duties, but you can override and extend the class methods to
perform specific actions for any particular config. It is also the job of the
`Parser` instance to call the next needed parser. In `ToolParser`, for example,
part of its parsing duties is to either call on the `OpenSearchParser` or
`NmslibParser`.

#### Conversion

Converting `YAML` files to Python Dictionaries is handled by
[PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

#### Validation

The validation is done by
[Cerberus](https://docs.python-cerberus.org/en/stable/), a lightweight Python
validation library.

The schemas of the config files are declared in `YAML` and can be found
[here](/okpt/io/config/schemas), which then Cerberus uses to build a `Validator`
object. We can then use the `Validator` object to either accept or reject a
parsed config file, depending on whether it conforms to the schema.

### Adding a new k-NN service

Adding a new k-NN service should be relatively simple. First, look over the
existing `Parser` classes to get a feel for how the Configuration Tree works.
Then, figure out how the existing Configuration Tree will be modified and add
the corresponding `Parser` classes. Most likely, you will just have to add a
`${new-knn-service}Parser` class and make sure the `ToolParser` class can choose
the new `Parser` when parsing.

## Testing

Here is some important testing terminology:

- **Measure**: A statistic or metric such `time_took` or `memory_used`.
- **Step / Test Step**: A single action made against a k-NN service. This could
  include making a single bulk index request to OpenSearch, refreshing the
  index, or creating an NMSLIB index. A **step** generally cannot be decomposed
  into smaller units. A **step** can be profiled by measuring the time before
  and after the step.
- **Step Measure**: A **measure** about a single step. These are often related
  to key performance indicators (KPI).
- **Test**: A collection of steps. A **test** can be profiled by
  adding/aggregating the measures of its steps. A **test** is a general process
  intended to be profiled such indexing or querying in OpenSearch but can be
  decomposed into smaller units.
- **Test Measure**: A statistic or measure about a test. Like a **step
  measure**, this could be `time_took` or `memory_used` but over the entire
  test, instead of a single step. These are often related to key performance
  indicators (KPI). Calculated by aggregating the **measures** of the test’s
  respective steps.
- **Run / Test Run**: An execution of a single **Test**. A user may want
  multiple runs of a **Test** to validate a hypothesis across a larger sample
  size of results.
- **Suite / Test Suite**: An execution of the tool, after running a Test the
  specified number of runs.

At the heart of the test framework are **steps**. The most important aspects of
a step are that they cannot be further decomposed and that they should be
measurable. Once we have steps, we can begin building **tests**. Tests are
merely aggregations of steps and designed to be easily composable. Tests are
what a user specifies in their configuration and they should be able to be run
multiple times.

We provide some sample steps and tests that represent some common use cases like
indexing and querying. Sample OpenSearch steps can be found
[here](/okpt/test/steps/opensearch.py) and sample tests can be found
[here](/okpt/test/tests/opensearch.py).

### Steps

Since steps need to be profiled and aggregated in a test, steps need a uniform
interface in order to be easily defined and aggregated. To do so, we provide a
base `Step` interface that should be extended for every new step. After
extending the base `Step`, you need to define the `label` and `measures`
attributes which define the name of the step and the metrics that it should
profile. The available `measures` are the profile decorators found in the
[`profile` module](/okpt/test/profile.py). For now, we only support the `took`
measure. Lastly, the actual step logic should go in an overriden `_action`
method which gets profiled in the `execute` method.

### Tests

Similar to steps, tests also need to have a uniform interface to be easily
defined and aggregated, so we provide a base `Test` class that should be
extended for new tests. Besides defining a test's steps, it also requires some
setup and cleanup. There are 4 types of these actions: pre-suite `setup`,
post-suite `cleanup`, pre-run `setup`, and post-run `cleanup`. Pre/post-suite
actions only occur once before and after all of the tests runs and pre/post-run
actions occur before and after every test run. Pre/post-suite actions are
defined in the `setup` and `_cleanup` methods, while pre/post-run actions should
be specified in the `_run_steps` method.

Test steps should be specified by executing the steps and storing their results
in the `self.step_results` list which will get aggregated after a test is ran.

### Test Runner

The tests are then managed by the `TestRunner` class which runs and aggregates
the test results. The specific tests are discoverable by the
[`TestFactory` class](/okpt/test/tests/factory.py).

### Adding New Tests

To add new tests, you first need to add new steps (using the provided steps as a
guide) if the provided steps are insufficient. Then create a new test (using the
provided tests as a guide) and define the necessary setup/cleanup actions and
steps needed (by putting the results into `self.step_results`). Finally, make
the test discoverable by adding it to the `TestFactory` class.

## Docker

Running the tests on any machine can be hard to configure consistently and may
produce noisy test results, so we've containerized the performance tool with
[Docker](https://www.docker.com).

### Docker Image

We use one Docker image per k-NN service, i.e. one OpenSearch image, one NMSLIB
image, etc. The `Dockerfile` for these images can be found at
`docker/<service>/Dockerfile` and prepare the image to be able to run the
relevant services and tests. Each image also comes with an entrypoint script at
`scripts/<service>-entrypoint.sh` that performs container setup (e.g. starting
OpenSearch, running the tool).

### Docker Compose

The process of building/running a Docker image can be tedious, so we also use
[Docker Compose](https://docs.docker.com/compose/) to help setup the container
environment.

We use Docker Compose to:

- pass arguments to the testing tool
- pass arguments to `docker build`
- mount host directories such as `dataset`, `config`, `output` onto the
  container
- run tests with one `docker compose up` command

To run an OpenSearch indexing test, you can run:

```
docker compose --file docker/opensearch/docker-compose.yml --env-file docker/opensearch/docker-compose.env --project-directory . up
```

There are a few Docker Compose components:

#### `docker-compose.yml`

The `docker-compose.yml` is the main config file for Docker Compose and the
`docker compose up` command.

#### `docker-compose.env`

The `docker-compose.env` file is used to pass arguments into the
`docker-compose.yml` file.

#### `container.env`

The `container.env` file is used to pass arguments into the Docker container,
which can be used in the entrypoint point script and subsequently, the
performance tool.

These three files should be defined per k-NN service and we have provided
default values in the `docker/<service>/` directory. The provided Docker Compose
setup are just examples and will likely needed to be modified, particularly the
`*.env` files.

### Adding a new k-NN Service

To extend the Docker setup for a new k-NN service, you first need to provide a
Docker image with a `Dockerfile` and its `<service>-entrypoint.sh` script. Then
to integrate with the Docker Compose setup, you need to define the
`docker-compose.yml`, `docker-compose.env`, and `container.env` files with
reasonable defaults.
