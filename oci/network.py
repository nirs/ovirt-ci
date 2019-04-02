import functools
import logging
import socket
import time

import gi
gi.require_version('NM', '1.0')
from gi.repository import GLib, Gio, NM

log = logging.getLogger("network")


class ConnectivityTimeout(Exception):
    """
    Timed out waiting for network connectivity.
    """


def connected():
    # It seems that we must create new client for every check, or we may
    # get stale state.
    client = NM.Client.new(None)

    state = client.get_state()
    log.debug("NetworkManager state: %s", state)
    if state < NM.State.CONNECTING:
        return False

    try:
        connectivity = client.check_connectivity()
    except GLib.Error as e:
        # Sometimes this fails with:
        # GLib.Error: g-io-error-quark: Timeout was reached (24)
        if not e.matches(Gio.io_error_quark(), Gio.IOErrorEnum.TIMED_OUT):
            raise

        log.debug("Timed out checking connectivity: %s", e)
        return False

    log.debug("NetworkManager connectivity: %s", connectivity)
    return connectivity == NM.ConnectivityState.FULL


def wait_until_connected(timeout, interval=10):
    deadline = time.time() + timeout

    log.info("Waiting for network connectivity")

    while not connected():
        now = time.time()
        if now >= deadline:
            raise ConnectivityTimeout(
                "Timeout waiting for network connectivity")

        wait = min(interval, deadline - now)
        time.sleep(wait)

    log.info("Network connectivity restored")


def retry(timeout=180, interval=10):
    """
    Return a decorator that wait for network connectivity for timeout seconds
    if the decorated function seems to fail because network connectivity was
    lost.
    """
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*a, **kw):
            while True:
                try:
                    return func(*a, **kw)
                except socket.error as e:
                    if connected():
                        raise
                    log.debug("%s: %s", e.__class__.__name__, e)
                    wait_until_connected(timeout, interval)

        return wrapper

    return decorator
