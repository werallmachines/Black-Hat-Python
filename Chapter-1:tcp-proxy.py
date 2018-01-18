#!/usr/bin/env python2
#TCP Proxy from Chapter-1 of Black Hat Python

import sys, socket, threading

def server_loop(local_host, local_port, remote_host,
                 remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((local_host, local_port))
    except:
        print "[*] Failed to listen on {}:{}".format(local_host, local_port)
        print "[*] Check for other listening sockets or correct permissions."
        sys.exit(0)

    print "[*] Listening on {}:{}".format(local_host, local_port)
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print "[==>] Received incoming connection from {}:{}".format(addr[0], addr[1])
        proxy_thread = threading.Thread(target=proxy_handler,
                                         args=(client_socket, remote_host, remote_port))
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port):
    '''
    loop that listens for inbound data from both ends
    of connection. unlike book, coded to automatically
    listen for banner msg first, then go into loop
    '''
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    remote_socket.connect((remote_host, remote_port))

    try:
        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            print "[<==] Sending {} bytes to localhost.".format(len(remote_buffer))
            client_socket.send(remote_buffer)
            remote_buffer = ""
    except:
        pass

    while True:
        local_buffer = receive_from(client_socket)

        if local_buffer:
            print "[==>] Received {} bytes from localhost.".format(len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote host."
            remote_buffer = receive_from(remote_socket)
            local_buffer = ""

        if remote_buffer:
            print "[<==] Received {} bytes from remote host.".format(len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print "[<==] Sent to localhost."
            remote_buffer = ""

        if not local_buffer or not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print "[*] No more data. Closing connection."

            break

def hexdump(src, length=16):
    '''
    hexdumper gotten from
    http://code.activestate.com/recipes/142812-hex-dumper/
    '''
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X  %-*s  %s" % (i, length*(digits + 1), hexa, text) )

    print b'\n'.join(result)

def receive_from(connection):
    '''
    receives the actual packets from the socket.
    reused for both ends of connection
    '''
    buffer = ""
    connection.settimeout(3)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            else:
                buffer += data
    except:
        pass
    return buffer


def request_handler(buffer):
    '''
    for you to modify packets manually if needed
    '''
    return buffer

def response_handler(buffer):
    '''
    for you to modify packets manually if needed
    '''
    return buffer

def main():
    '''
    parse command line manually then start 
    the server loop
    '''
    if len(sys.argv[1:]) != 4:
        print "Usage: /tcp-proxy.py [localhost] [localport] [remotehost] [remoteport]"
        print "Example: ./tcp-proxy.py 127.0.0.1 9000 10.10.10.10 9000"
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    server_loop(local_host, local_port, remote_host, remote_port)

if __name__ == "__main__":
    main()
