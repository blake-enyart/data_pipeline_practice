
# Welcome to your CDK Python project!

This is a blank project for Python development with CDK.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

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
$ poetry install
```

Ensure that the pre-commit hooks are configured using the following command
```
$ inv install-hooks
```


Configure the `tasks.py` file such that the AWS_PROFILE is set to your AWS CLI profile which you want to work out of.

At this point you can now determine the names of the available stacks.

```
$ inv ls
```
From this list, synthesize the CloudFormation template for this code as follows.

```
$ inv synth -s streaming-data-pipeline-s3-<username>
```

At this point, you are ready to deploy the CDK application to AWS.
```
$ inv deploy -s streaming-data-pipeline-s3-<username>
```

To add additional dependencies, for example other CDK libraries, just use
`poetry add <library name>` command.

## Useful commands

 * `inv ls`          list all stacks in the app
 * `inv synth`       emits the synthesized CloudFormation template
 * `inv deploy`      deploy this stack to your default AWS account/region
 * `inv diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
