from httpserverhandler import run_server
from socketserverhandler import run_socket_server
import logging
from multiprocessing import Process

format_str = '%(asctime)s %(process)d %(message)s'
logging.basicConfig(format=format_str, level=logging.DEBUG, datefmt='%H:%M:%S')

if __name__ == "__main__":
    logging.info('Starting servers...')
    http = Process(target=run_server)
    socket = Process(target=run_socket_server)

    http.start()
    socket.start()

    http.join()
    socket.join()

