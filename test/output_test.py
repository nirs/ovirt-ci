from __future__ import print_function

import sys
import pytest
from six import StringIO
from ovirt_ci import output


class TTY(StringIO):

    def isatty(self):
        return True


def test_success():
    f = TTY()
    o = output.TextOutput(5, file=f)
    o.step("Getting change %s info", "54321")
    o.step("Starting build-artifacts job")
    o.info(("project", "vdsm"), ("branch", "ovirt-4.3"), ("patchset", 2))
    o.step("Starting system tests %s suite", "basic")
    o.step("Waiting for job %s", "https://jenkins.ovirt.org/job/98765")
    o.success("Job completed successfully!")

    out = f.getvalue()
    assert out == """\
[ 1/5 ] Getting change 54321 info
[ 2/5 ] Starting build-artifacts job
        project: vdsm   branch: ovirt-4.3   patchset: 2
[ 3/5 ] Starting system tests basic suite
[ 4/5 ] Waiting for job https://jenkins.ovirt.org/job/98765
[ 5/5 ] {}Job completed successfully!{}
""".format(output.GREEN, output.RESET)

    print()
    print(out)


def test_failure():
    f = TTY()
    o = output.TextOutput(4, file=f)
    o.step("Getting change %s info", "54321")
    o.step("Starting system tests %s suite", "basic")
    o.step("Waiting for job %s", "https://jenkins.ovirt.org/job/98765")
    o.failure("Oh dear, job failed")

    out = f.getvalue()
    assert out == """\
[ 1/4 ] Getting change 54321 info
[ 2/4 ] Starting system tests basic suite
[ 3/4 ] Waiting for job https://jenkins.ovirt.org/job/98765
[ 4/4 ] {}Oh dear, job failed{}
""".format(output.RED, output.RESET)

    print()
    print(out)


def test_early_failure():
    f = TTY()
    o = output.TextOutput(4, file=f)
    o.step("Getting change %s info", "54321")
    o.step("Starting system tests %s suite", "basic")
    o.failure("Cannot start system tests")

    out = f.getvalue()
    assert out == """\
[ 1/4 ] Getting change 54321 info
[ 2/4 ] Starting system tests basic suite
[ 3/4 ] {}Cannot start system tests{}
""".format(output.RED, output.RESET)

    print()
    print(out)


def test_no_tty():
    f = StringIO()
    o = output.TextOutput(2, file=f)
    o.step("First step")
    o.success("It worked!")

    assert f.getvalue() == """\
[ 1/2 ] First step
[ 2/2 ] It worked!
"""
