import sys

GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"


class TextOutput(object):

    def __init__(self, file=sys.stdout):
        self._file = file

    def step(self, fmt, *args):
        self._write(fmt, args)

    def failure(self, fmt, *args):
        self._write(fmt, args, color=RED)

    def success(self, fmt, *args):
        self._write(fmt, args, color=GREEN)

    def _write(self, fmt, args, color=None):
        s = fmt % args

        if self._file.isatty() and color:
            s = color + s + RESET

        self._file.write(s + "\n")
        self._file.flush()
