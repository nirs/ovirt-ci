import sys

GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"

def info(s, *args):
    _output(s, args)

def failure(s, *args):
    _output(s, args, color=RED)

def success(s, *args):
    _output(s, args, color=GREEN)

def _output(fmt, args, color=None):
    s = fmt % args

    if sys.stdout.isatty():
        s = _colorize(s, color)

    sys.stdout.write(s + "\n")
    sys.stdout.flush()

def _colorize(s, color):
    if color is None:
        return s

    return color + s + RESET
