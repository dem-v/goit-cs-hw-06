import asyncio
import websockets
from dbhandler import DbHandler
from ast import literal_eval
import logging
format_str = '%(asctime)s %(process)d %(message)s'
logging.basicConfig(format=format_str, level=logging.DEBUG, datefmt='%H:%M:%S')


class SocketServer:
    def __init__(self):
        self.db = DbHandler()

    async def hello(self, websocket):
        msg = await websocket.recv()
        logging.debug(f'<<< {msg}')
        decoded_msg = literal_eval(msg)
        try:
            if self.db.save_message(decoded_msg['username'], decoded_msg['message']):
                await websocket.send("OK")
                logging.debug('>>> OK')
            else:
                await websocket.send("FAIL")
                logging.debug('>>> FAIL')
        except Exception as e:
            await websocket.send("FAIL")
            logging.debug(f'>>> FAIL; error {e}')

    async def runner(self):
        async with websockets.serve(self.hello, "app", 5000):
            await asyncio.Future()  # run forever


def run_socket_server():
    ss = SocketServer()
    logging.info('Socket server up')
    asyncio.run(ss.runner())


if __name__ == "__main__":
    run_socket_server()
