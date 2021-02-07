import configparser
import datetime as dt
import os
import sys
import tempfile
import time
from pathlib import Path

from invoke import task, Responder
from klaxon import klaxon

APP = "data_pipeline_practice"
AWS_PROFILE = "default"
AWS_REGION = "us-east-1"

# Must separate these by spaces and indicate directories with trailing /
BLACK_FILEPATH_STR = f"{APP}/ containers/ tests/"


@task
def clean(c):
    """Delete unused code."""

    c.run(r"find . -name \*.pyc -delete")

    c.run("rm shelves/*", warn=True)

    c.run("rm -rf cdk.out/*")


@task
def install_hooks(c):
    """Install git hooks."""

    c.run("pre-commit install")

    c.run("pre-commit install -t pre-push")

    # Optionally install commitizen CLI
    try:
        c.run("commitizen", hide=True)
    except:
        c.run("npm install -g commitizen")


@task
def uninstall_hooks(c):
    """Uninstall git hooks."""
    c.run("pre-commit uninstall")
    c.run("pre-commit uninstall -t pre-push")


@task(aliases=["black"])
def format(c):
    """Auto-format Python modules."""
    c.run(f"black *.py {BLACK_FILEPATH_STR}")


@task(aliases=["check-black"])
def check_formatting(c):
    """Check that files conform to black standards."""
    c.run(f"black --check *.py {BLACK_FILEPATH_STR}")


@task(optional=["stack"])
def deploy(
    c, profile=AWS_PROFILE, region=AWS_REGION, force=False, app=APP, stack=None
):
    """Deploy CDK CloudFormation stack(s)."""

    if stack:
        c.run(
            f"cdk deploy --profile={profile} {stack}"
            + (" --require-approval never" if force else ""),
            pty=True,
            env={"AWS_DEFAULT_REGION": region},
        )
        klaxon(title=app, subtitle="deployed CDK stack")
    else:
        print("Please provide a stack to deploy")


@task
def destroy(
    c, profile=AWS_PROFILE, region=AWS_REGION, force=False, app=APP, stack=None
):
    """Tear-down CDK CloudFormation stack(s)."""

    responder = Responder(
        pattern="Are you sure you want to delete.*", response="y\n"
    )

    if stack:
        c.run(
            f"cdk destroy --profile={profile} {stack}",
            pty=True,
            watchers=[responder] if force else [],
            env={"AWS_DEFAULT_REGION": region},
        )
        klaxon(title=app, subtitle="destroyed CDK stack")
    else:
        print("Please provide a stack to deploy")


@task(optional=["stack"])
def diff(c, profile=AWS_PROFILE, region=AWS_REGION, stack=None):
    """Compare current CDK stack to what was previously deployed."""

    if stack:
        c.run(
            f"cdk diff --profile={profile} {stack}",
            pty=True,
            env={"AWS_DEFAULT_REGION": region},
        )
    else:
        print("Please provide a stack to deploy")


@task
def ls(c, profile=AWS_PROFILE):
    """List of CDK stacks that are deployable"""

    c.run(f"cdk list --profile {profile}")


@task(optional=["stack"])
def synth(c, profile=AWS_PROFILE, region=AWS_REGION, stack=None):
    """Render CDK CloudFormation template."""

    if stack:
        c.run(
            f"cdk synth --profile={profile} {stack}",
            pty=True,
            env={"AWS_DEFAULT_REGION": region},
        )
    else:
        print("Please provide a stack to deploy")


@task
def test(c):
    """Runs test suite before committing code"""
    c.run("pytest", pty=True)


@task
def s3_bucket_sync(
    c, profile=AWS_PROFILE, source_bucket=None, sink_bucket=None
):
    """Sync an S3 bucket with another S3 bucket"""
    if not source_bucket or sink_bucket:
        source_bucket = "s3://deutsche-boerse-eurex-pds/2017-05-27/"
        sink_bucket = "s3://nutrien-blake-enyart-dev/dbg_pds_RAW/"
    c.run(f"aws --profile {profile} s3 sync {source_bucket}* {sink_bucket}*")
