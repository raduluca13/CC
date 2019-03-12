import socket
import _thread
import threading

import handlers

HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)

print('Serving HTTP on port %s ...' % PORT)

while True:
    client_connection, client_address = listen_socket.accept()
    # threading.Thread(target=handlers.handle_new_client, args=(client_connection, client_address)).start()
    handlers.handle_new_client(client_connection, client_address)

listen_socket.close()


