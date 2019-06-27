import sys
from mitmproxy import io, http
import typing  # noqa
import click

EXTRA_QUERY_ARG = "tk_poll_index"
requests = {}


class Writer:
    def __init__(self, path: str, writer_mode=False) -> None:
        self.writer_mode = writer_mode
        if self.writer_mode:
            self.f: typing.IO[bytes] = open(path, "wb")
            self.w = io.FlowWriter(self.f)

    def clientconnect(self, root_layer):
        client_port = root_layer.ctx.client_conn.address[1]
        click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " clientconnect")

    def clientdisconnect(self, root_layer):
        client_port = root_layer.ctx.client_conn.address[1]
        click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " clientdisconnect")

    def http_connect(self, flow: http.HTTPFlow):
        client_port = flow.client_conn.address[1]
        click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " http_connect")

    def request(self, flow: http.HTTPFlow) -> None:
        client_port = flow.client_conn.address[1]
        click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " request")
        print(f"request {client_port} {flow.request.url}")
        requests[client_port] = requests[client_port] + 1 if client_port in requests else 0
        if not self.writer_mode:
            flow.request.query[EXTRA_QUERY_ARG] = requests[client_port]

    def response(self, flow: http.HTTPFlow) -> None:
        client_port = flow.client_conn.address[1]
        click.echo(click.style(f"[{client_port}]", fg="cyan", bold=True) + " response")
        print(f"response {client_port} {flow.request.url}")
        if self.writer_mode:
            flow.request.query[EXTRA_QUERY_ARG] = requests[client_port]
            self.w.add(flow)

    def error(self, flow: http.HTTPFlow):
        if flow.request:
            print(f"connect error {flow.id}: {flow.request.url} --> {flow.request.host}")
        else:
            print(f"connect error {flow.id}")

    def done(self):
        print(f"Done, closing file")
        if self.writer_mode:
            self.f.close()


addons = [Writer("locust.bin", writer_mode=False)]
