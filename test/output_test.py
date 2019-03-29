import sys
import pytest
from six import StringIO
from oci import output


class TTY(StringIO):

    def isatty(self):
        return True


def test_info():
    f = TTY()
    o = output.TextOutput(f)
    o.info("msg")
    assert f.getvalue() == "msg\n"


def test_success():
    f = TTY()
    o = output.TextOutput(f)
    o.success("msg")
    assert f.getvalue() == output.GREEN + "msg" + output.RESET + "\n"


def test_failure():
    f = TTY()
    o = output.TextOutput(f)
    o.failure("msg")
    assert f.getvalue() == output.RED + "msg" + output.RESET + "\n"


def test_no_tty(capsys):
    f = StringIO()
    o = output.TextOutput(f)
    o.success("msg")
    assert f.getvalue() == "msg\n"


def test_args():
    f = TTY()
    o = output.TextOutput(f)
    o.success("msg %s %s", 1, 2)
    assert f.getvalue() == output.GREEN + "msg 1 2" + output.RESET + "\n"
