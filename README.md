
# Welcome to the CDK Data Pipeline!

This project is a data pipeline illustrating some of the best practices in pipeline manage such as: unit testing, monitoring and observability, and serverless archiecture. This project is built utilizing CDK(Python), Docker, Former2, and the AWS Console Recorder.

Ultimately, this project is here to illustrate just what is possible when leveraging the AWS CDK to further the goal of combining infrastucture, CI/CD, and development into a singular practice gaining popularity known as DataOps.

Initially, this project was developed as a single stack. As the complexity grew, I decided to break the project into several stacks with inter-stack dependencies. All of this is governed by the constraint that all stacks are within the same account and region. Once, I broke the project up into several stacks, I opted to introduce a [monitoring stack](../main/data_pipeline_practice/monitoring_stack.py) which functions to create a CloudWatch alarm which monitors the throughput of the Kinesis Firehose created in the [data pipeline stack](../main/data_pipeline_practice/data_pipeline_stack.py).

Below is the reference architecture for this project. All of this was developed over the course of a weekend. Hopefully, this illustrates some of the strengths of combining infrastructure and development into a singular practice.

## Reference Architecture
<p align="center">
    <img src=static/images/Reference%20Architectures%20-%20Data%20Pipeline%20-%20Architecture.jpg  width="400" height="350" alt="Reference Architecture">
</p>

## Getting Started

Prior to configuring your virtualenv, ensure you have the [invoke](http://www.pyinvoke.org/) and [poetry](https://python-poetry.org/) libraries installed globally for your python version.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
$ poetry install
```

Ensure that the pre-commit hooks are configured using the following command
```
$ inv install-hooks
```
Note: this git workflow will now look something like:
* `git add <file>`
* `git commit`
* `git add .` -- if there are code corrections
* `git commit` -- to verify that the pre-commit hooks are resolved
* `:q` -- to exit the message prompt and utilize the more robust command below
* `git cz` -- to make a descriptive commit to the repo

Configure the `tasks.py` file such that the AWS_PROFILE is set to your AWS CLI profile which you want to work out of.

At this point you can now determine the names of the available stacks.

```
$ inv ls
```
It is recommended that you deploy the stacks in the following order using `inv deploy -s <stack name>`:
* `networking-<username>-<stage>`
* `data-pipeline-<username>-<stage>`
* `stream-app-<username>-<stage>`
* `monitoring-<username>-<stage>`

To add additional dependencies, for example other CDK libraries, just use
`poetry add <library name>` command.

## Useful commands

 * `inv ls`          list all stacks in the app
 * `inv synth`       emits the synthesized CloudFormation template
 * `inv deploy`      deploy this stack to your default AWS account/region
 * `inv diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
