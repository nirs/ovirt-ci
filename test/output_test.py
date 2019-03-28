import pytest
import sys
from oci import output

GREEN_OUTPUT = output.GREEN + "msg" + output.RESET + "\n"
RED_OUTPUT = output.RED + "msg" + output.RESET + "\n"
GREEN_OUTPUT_WITH_ARGS = output.GREEN + "msg 1 2" + output.RESET + "\n"


def test_info(capsys):
    output.info("msg")
    captured = capsys.readouterr()
    assert captured.out == "msg\n"


def test_success(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    output.success("msg")
    captured = capsys.readouterr()
    assert captured.out == GREEN_OUTPUT


def test_failure(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    output.failure("msg")
    captured = capsys.readouterr()
    assert captured.out == RED_OUTPUT


def test_color_no_tty(capsys):
    output.success("msg")
    captured = capsys.readouterr()
    assert captured.out == "msg\n"


def test_color_with_args(monkeypatch, capsys):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    output.success("msg %s %s", "1", "2")
    captured = capsys.readouterr()
    assert captured.out == GREEN_OUTPUT_WITH_ARGS
