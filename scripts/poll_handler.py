"""
This script adds a fake parameter to all requests that already exists in the replay file

The idea here is that multiple connections will connect to the proxy using a different port
so when that happens we increment a counter of requests for the port and add them to the replay file

"""

from mitmproxy import io, http, exceptions, ctx
import typing  # noqa
import click
import threading

EXTRA_QUERY_ARG = "tk_poll_index"
requests = {}
DEBUG_MODE = True
lock = threading.Lock()

class Writer:
    def __init__(self) -> None:
        self.file_open = False
        self.record_mode = False
        self.replay_file = None
        self.flow_writer = None
        self.verbose = DEBUG_MODE

    def load(self, loader):
        loader.add_option(
            name="record",
            typespec=str,
            default='False',
            help="Records the file",
        )
        loader.add_option(
            name="replayfile",
            typespec=str,
            default='',
            help="Path to the replay file",
        )

    def running(self):
        print(f"Record mode is {ctx.options.record} and path file is {ctx.options.replayfile}")
        self.record_mode = ctx.options.record and ctx.options.record.lower() == 'true'
        with lock:
            if not self.file_open and self.record_mode:
                if not ctx.options.replayfile:
                    print(f"Need to specify a file path with --set replayfile=<path/to/file>")
                    raise exceptions.OptionsError("Need to specify a file path with --set replayfile=<path/to/file>")
                print(f"Opening {ctx.options.replayfile} in write mode")
                self.replay_file: typing.IO[bytes] = open(ctx.options.replayfile, "wb")
                self.flow_writer = io.FlowWriter(self.replay_file)
                self.file_open = True

    def clientconnect(self, root_layer):
        if self.verbose:
            client_port = root_layer.ctx.client_conn.address[1]
            click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " clientconnect")

    def clientdisconnect(self, root_layer):
        if self.verbose:
            client_port = root_layer.ctx.client_conn.address[1]
            click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " clientdisconnect")

    def http_connect(self, flow: http.HTTPFlow):
        if self.verbose:
            client_port = flow.client_conn.address[1]
            click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " http_connect")

    def request(self, flow: http.HTTPFlow) -> None:
        client_port = flow.client_conn.address[1]
        if self.verbose:
            click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " request")
            print(f"request {client_port} {flow.request.url}")
        requests[client_port] = requests[client_port] + 1 if client_port in requests else 0
        if not self.record_mode:
            flow.request.query[EXTRA_QUERY_ARG] = requests[client_port]

    def response(self, flow: http.HTTPFlow) -> None:
        client_port = flow.client_conn.address[1]
        if self.verbose:
            click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " response")
            print(f"response {client_port} {flow.request.url}")
        if self.record_mode:
            flow.request.query[EXTRA_QUERY_ARG] = requests[client_port]
            self.flow_writer.add(flow)

    def error(self, flow: http.HTTPFlow):
        if flow.request:
            print(f"connect error {flow.id}: {flow.request.url} --> {flow.request.host}")
        else:
            print(f"connect error {flow.id}")

    def done(self):
        if self.record_mode:
            print(f"Done, closing file")
            self.replay_file .close()


addons = [Writer()]
