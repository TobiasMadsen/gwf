from ..cli import pass_graph, pass_backend

from werkzeug import serving
from werkzeug.wrappers import Request, Response
import socket
import click
import sys


@click.command()
@pass_graph
@pass_backend
def board(backend, graph):
    
    # Create Werkzeug App
    gb_app = gwfBoard(backend, graph)
    
    # Send app to simple webserver
    run_simple_server(gb_app)
    
    for t in graph.targets:
        print(t,'\n')
        

class gwfBoard(object):
    def __init__(self, backend, graph):
        self.graph = graph
        self.backend = backend
        #self.redis = redis.Redis(config['redis_host'], config['redis_port'])
    
    def dispatch_request(self, request):
        response = "\n".join(self.graph.targets)
        return Response(response)
    
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def make_simple_server(gb_app, host=None, port=None):
    """Create an HTTP server for GWFBoard.
    Args:
      gb_app: The GWFBoard WSGI application to create a server for.
      host: Indicates the interfaces to bind to ('::' or '0.0.0.0' for all
          interfaces, '::1' or '127.0.0.1' for localhost). A blank value ('')
          indicates protocol-agnostic all interfaces. If not specified, will
          default to the flag value.
      port: The port to bind to (0 indicates an unused port selected by the
          operating system). If not specified, will default to the flag value.
    Returns:
      A tuple of (server, url):
        server: An HTTP server object configured to host GWFBoard.
        url: A best guess at a URL where GWFBoard will be accessible once the
          server has been started.
    Raises:
      socket.error: If a server could not be constructed with the host and port
        specified. Also logs an error message.
    """
    if host is None:
        host = '127.0.0.1' # FLAGS.host
    if port is None:
        port = 5000 # FLAGS.port
    
    try:
        if host:
            # The user gave us an explicit host
            server = serving.make_server(host, port, gb_app, threaded=True)
            if ':' in host and not host.startswith('['):
                # Display IPv6 addresses as [::1]:80 rather than ::1:80
                final_host = '[{}]'.format(host)
            else:
                final_host = host
        else:
            # We've promised to bind to all interfaces on this host. However, we're
            # not sure whether that means IPv4 or IPv6 interfaces.
            try:
                # First try passing in a blank host (meaning all interfaces). This,
                # unfortunately, defaults to IPv4 even if no IPv4 interface is available
                # (yielding a socket.error).
                server = serving.make_server(host, port, gb_app, threaded=True)
            except socket.error:
                # If a blank host didn't work, we explicitly request IPv6 interfaces.
                server = serving.make_server('::', port, gb_app, threaded=True)
            final_host = socket.gethostname()
        server.daemon_threads = True
    except socket.error as socket_error:
        if port == 0:
            msg = 'GWFBoard unable to find any open port'
        else:
            msg = (
                'GWFBoard attempted to bind to port %d, but it was already in use'
                % port)
        print(msg)
        raise socket_error
    server.handle_error = _handle_error
    final_port = server.socket.getsockname()[1]
    gwfboard_url = 'http://%s:%d' % (final_host, final_port)
    return server, gwfboard_url

def run_simple_server(gb_app):
    """Run a GWFBoard HTTP server, and print some messages to the console."""
    try:
        server, url = make_simple_server(gb_app)
    except socket.error:
        # An error message was already logged
        # TODO(@jart): Remove log and throw anti-pattern.
        sys.exit(-1)
    sys.stderr.write('GwfBoard %s at %s (Press CTRL+C to quit)\n' %
                   ("0.1", url))
    sys.stderr.flush()
    server.serve_forever()


# Kludge to override a SocketServer.py method so we can get rid of noisy
# EPIPE errors. They're kind of a red herring as far as errors go. For
# example, `curl -N http://localhost:6006/ | head` will cause an EPIPE.
def _handle_error(unused_request, client_address):
    exc_info = sys.exc_info()
    e = exc_info[1]
