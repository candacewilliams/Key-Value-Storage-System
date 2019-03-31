# This code uses Python 2.7. These imports make the 2.7 code feel a lot closer# to Python 3. (They're also good changes to the language!)
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import library

# Where to find the server. This assumes it's running on the smae machine
# as the proxy, but on a different port.
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 7777

# The port that the proxy server is going to occupy. This could be the same
# as SERVER_PORT, but then you couldn't run the proxy and the server on the
# same machine.
LISTENING_PORT = 8888

# Cache values retrieved from the server for this long.
MAX_CACHE_AGE_SEC = 60.0  # 1 minute

def ForwardCommandToServer(command, server_addr, server_port):
    
    client_socket = library.CreateClientSocket(server_addr, server_port)
    client_socket.send(command + '\n')
    server_response = library.ReadCommand(client_socket)
    client_socket.close()

    return server_response + '\n'

def CheckCachedResponse(command_line, cache):
    cmd, name, text = library.ParseCommand(command_line)
    
    if cmd == "PUT":
        cache.StoreValue(name,text)

        ForwardCommandToServer(command_line, SERVER_ADDRESS, SERVER_PORT)
    
        return None

    elif cmd == "GET":
        if name in cache:
            return cache[name]
        else:
            ForwardCommandToServer(command_line, SERVER_ADDRESS, SERVER_PORT)
            
def ProxyClientCommand(sock, server_addr, server_port, cache):
    command_line = library.ReadCommand(sock)
    cmd, name, value = library.ParseCommand(command_line)

    if cmd == 'PUT':
        server_response = ForwardCommandToServer(command_line, server_addr, server_port)
        cache.StoreValue(name, server_response)

    elif (cmd == 'GET'):
        server_response = cache.GetValue(name)
        if server_response == None:
            server_response = ForwardCommandToServer(command_line, server_addr, server_port)

    else:
        server_response = ForwardCommandToServer(command_line, server_addr, server_port)

    sock.send(server_response)


def main():
    # Listen on a specified port...
    server_sock = library.CreateServerSocket(LISTENING_PORT)
    cache = library.KeyValueStore()

    # Accept incoming commands indefinitely.
    while True:
        # Wait until a client connects and then get a socket that connects to the
        # # client.
        client_sock, (address, port) = library.ConnectClientToServer(server_sock)
        print('Received connection from %s:%d' % (address, port))
        ProxyClientCommand(client_sock, SERVER_ADDRESS, SERVER_PORT, cache)
        
        client_sock.close()
    
main()
