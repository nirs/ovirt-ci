import sys

GREEN = "\033[1;32m"
RED = "\033[1;31m"
RESET = "\033[0m"


class TextOutput(object):

    def __init__(self, steps, file=sys.stdout):
        self._steps = steps
        self._file = file
        self._current = 0

    def step(self, fmt, *args):
        self._current += 1
        self._write_title(fmt, args)

    def info(self, *pairs):
        content = "   ".join("{}: {}".format(k, v) for k, v in pairs)
        line = "        {}\n".format(content)
        self._write(line)

    def failure(self, fmt, *args):
        self._current += 1
        self._write_title(fmt, args, color=RED)

    def success(self, fmt, *args):
        self._current += 1
        self._write_title(fmt, args, color=GREEN)

    def _write_title(self, fmt, args, color=None):
        msg = fmt % args

        if self._file.isatty() and color:
            msg = color + msg + RESET

        line = "[ {}/{} ] {}\n".format(self._current, self._steps, msg)
        self._write(line)

    def _write(self, s):
        self._file.write(s)
        self._file.flush()
