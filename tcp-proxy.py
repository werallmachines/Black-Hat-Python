#!/usr/bin/env python2

import sys, socket, threading

def server_loop(local_host, local_port, remote_host,
                 remote_port, receive_first):
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((local_host, local_port))


def proxy_handler(client_socket, remote_host, remote_port,
                  receive_first):
remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
remote_socket.connect((remote_host, remote_port))

if receive_first:
    remote_buffer = receive_from(remote_socket)
    hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)

    if remote_buffer:
        print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
        client_socket.send(remote_buffer)

while True:
    local_buffer = receive_from(client_socket)

    if local_buffer:
        print "[==>] Received {} bytes from localhost.".format(len(local_buffer))
        hexdump(local_buffer)
        local_buffer = request_handler(local_buffer)
        remote_socket.send(local_buffer)
        print "[==>] Sent to remote host."
        remote_buffer = receive_from(remote_socket)

    if remote_buffer:
        print "[<==] Received {} bytes from remote host.".format(len(remote_buffer))
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        client_socket.send(remote_buffer)
        print "[<==] Sent to localhost."

    if not local_buffer or not remote_buffer:
        client_socket.close()
        remote_socket.close()
        print "[*] No more data. Closing connection."

        break

def hexdump(src, length=16):
    results = []
    digits 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b"%04X  %-*s  %s" % (i, length*(digits + 1), hexa, text) )

    print b'\n'.join(result)

def receive_from(connection):
    buffer =""
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
    return buffer

def response_handler(buffer):
    return buffer

def main():
    

