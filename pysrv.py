import threading
import webbrowser
import BaseHTTPServer
import SimpleHTTPServer
from SocketServer import ThreadingMixIn

PORT = 8080

class TestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))        
        data_string = self.rfile.read(length)
        print data_string[:50]
        self.wfile.write("Got " + data_string)

class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""
        
def start_server():
    """Start the server."""
    server_address = ("", PORT)
    server = ThreadedHTTPServer(server_address, TestHandler)
    print 'Starting server, <Ctrl-C> to stop'
    server.serve_forever()

if __name__ == "__main__":
    start_server()