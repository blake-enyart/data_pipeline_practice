import configparser
import datetime as dt
import os
import sys
import tempfile
import time
from pathlib import Path

from invoke import task, Responder
from klaxon import klaxon


@task
def clean(c):
    """Delete unused code."""

    c.run("find . -name \*.pyc -delete")

    c.run("rm shelves/*", warn=True)

    c.run("rm -rf cdk.out/*")


@task
def install_hooks(c):
    """Install git hooks."""

    c.run("pre-commit install")

    c.run("pre-commit install -t pre-push")

    # # this fixes a potentially broken shebang line in git hooks

    # for hook in Path(".git", "hooks").iterdir():

    #     hook.write_text(
    #         hook.read_text().replace(
    #             "#!/usr/bin/env python3.8", "#!/usr/bin/env python3"
    #         )
    #     )


@task
def uninstall_hooks(c):
    """Uninstall git hooks."""
    c.run("pre-commit uninstall")
    c.run("pre-commit uninstall -t pre-push")


@task(aliases=["black"])
def format(c):
    """Auto-format Python modules."""
    c.run("black *.py data_pipeline_practice/")


@task(aliases=["check-black"])
def check_formatting(c):
    """Check that files conform to black standards."""
    c.run("black --check *.py data_pipeline_practice/")


@task
def deploy(c, profile="nutrien", region="us-east-2", force=False):
    """Deploy cloudformation stack(s)."""

    c.run(
        f"cdk deploy --profile={profile} '*'"
        + (" --require-approval never" if force else ""),
        pty=True,
        env={"AWS_DEFAULT_REGION": region},
    )

    klaxon(title="nutrien-data-infra", subtitle="deployed cdk stack")


@task
def destroy(c, profile="nutrien", region="us-east-2", force=False):
    """Tear-down cloudformation stack(s)."""

    responder = Responder(
        pattern="Are you sure you want to delete.*", response="y\n"
    )

    c.run(
        f"cdk destroy --profile={profile}",
        pty=True,
        watchers=[responder] if force else [],
        env={"AWS_DEFAULT_REGION": region},
    )

    klaxon(title="nutrien-data-infra", subtitle="destroyed cdk stack")


@task
def diff(c, profile="nutrien", region="us-east-2"):
    """Compare current cdk stack to what was previously deployed."""

    c.run(
        f"cdk diff --profile={profile}",
        pty=True,
        env={"AWS_DEFAULT_REGION": region},
    )


@task
def synth(c, profile="nutrien", region="us-east-2"):
    """Render cdk cloudformation template."""

    c.run(
        f"cdk synth --profile={profile}",
        pty=True,
        env={"AWS_DEFAULT_REGION": region},
    )
