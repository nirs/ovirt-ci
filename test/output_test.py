import sys
import pytest
from oci import output


def test_info(capsys):
    output.info("msg")
    captured = capsys.readouterr()
    assert captured.out == "msg\n"


def test_success(capsys):
    sys.stdout.isatty = lambda: True
    output.success("msg")
    captured = capsys.readouterr()
    assert captured.out == output.GREEN + "msg" + output.RESET + "\n"


def test_failure(capsys):
    sys.stdout.isatty = lambda: True
    output.failure("msg")
    captured = capsys.readouterr()
    assert captured.out == output.RED + "msg" + output.RESET + "\n"


def test_color_no_tty(capsys):
    output.success("msg")
    captured = capsys.readouterr()
    assert captured.out == "msg\n"


def test_color_with_args(capsys):
    sys.stdout.isatty = lambda: True
    output.success("msg %s %s", "1", "2")
    captured = capsys.readouterr()
    assert captured.out == output.GREEN + "msg 1 2" + output.RESET + "\n"
