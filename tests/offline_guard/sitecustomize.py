"""Loaded by Python in CI (including CLI subprocesses) to prohibit network access."""
import socket


def denied(*args, **kwargs):
    raise AssertionError('network access is prohibited during offline verification')


socket.create_connection = denied
socket.socket.connect = denied
socket.socket.connect_ex = denied
