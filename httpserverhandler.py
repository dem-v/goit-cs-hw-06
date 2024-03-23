from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import asyncio
import websockets
import logging
format_str = '%(asctime)s %(process)d %(message)s'
logging.basicConfig(format=format_str, level=logging.DEBUG, datefmt='%H:%M:%S')


class HttpHandler(BaseHTTPRequestHandler):
    SOCKET_URI = 'ws://app:5000'

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        match pr_url.path:
            case '/':
                self.send_html_file('index.html')
            case '/message.html':
                self.send_html_file('message.html')
            case '/style.css':
                self.send_static_file('style.css')
            case '/logo.png':
                self.send_static_file('logo.png')
            case _:
                self.send_html_file('error.html', 404)

        logging.debug(pr_url)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename, status=200):
        self.send_response(status)
        mime_type, _ = mimetypes.guess_type(filename)
        self.send_header('Content-type', mime_type if mime_type else 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        logging.debug(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        logging.debug(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        logging.debug(data_dict)
        if self.send_message_to_socket(str(data_dict)):
            self.send_response(302)
            self.send_header('Location', '/message.html')
            self.end_headers()
        else:
            self.send_response(302)
            self.send_header('Location', '/error.html')
            self.end_headers()

    async def send_message_async(self, message: str) -> bool:
        uri = self.SOCKET_URI
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            resp = await websocket.recv()
            if resp != 'OK':
                logging.info(f'Error: {resp}')
                return False
            return True

    def send_message_to_socket(self, message: str) -> bool:
        return asyncio.run(self.send_message_async(message))


def run_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        logging.info('HTTP server up')
        http.serve_forever()
    except KeyboardInterrupt:
        logging.info('Shutting down...')
    except Exception as e:
        logging.warning(f'Server error: {e}')
    finally:
        http.server_close()


if __name__ == '__main__':
    run_server()
