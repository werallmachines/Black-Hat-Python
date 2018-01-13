#!/usr/bin/env python2.7

import sys, struct, socket, argparse, threading, subprocess

file_buffer = ""
listen = ""
cmd = ""
upload = True
execute = ""
target = ""
upload_destination = "/home/ubuntu/bob"

frame_struct = struct.Struct("!I")

def parse_cmd_line():
    global listen
    global cmd
    global execute
    global target
    global upload

    parser = argparse.ArgumentParser(description="NC replacement tool")
    parser.add_argument("-l", action="store_true",
                        help="Set PyCat to listen on given [IP]:[port]")
    parser.add_argument("-c", metavar="cmd", help="Initialize command shell")
    parser.add_argument("-e", metavar="execute", help="Execute file upon connection")
    parser.add_argument("IP", help="Connect to/bind to (0.0.0.0 for all interfaces)")
    parser.add_argument("p", type=int, help="TCP port to use")
    #parser.add_argument("-u", metavar="upload",
                        #help="Upon connection upload and write file to [destination]")
    args = parser.parse_args()

    listen = args.l
    cmd = args.c
    execute = args.e
    target = (args.IP, args.p)
    #upload = args.u

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        client.connect((target[0], target[1]))
    except:
        print "test"

def server_loop():
    global target

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target[0], target[1]))
    server.listen(2)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def run_cmd(cmd):
    pass

def client_handler(client_socket):
    global upload
    global execute
    global cmd

    """
    If -u is chosen at target end, will receive bytes
    and try to write them out to file.
    """
    if upload:
        file_buffer = ""

        try:
            while True:
                data = find_length(client_socket)
                if not data:
                   write_buffer(client_socket, file_buffer)
                else:
                    file_buffer += data
        except EOFError:
            print "Client socket has closed"
        finally:
            client_socket.close()

def write_buffer(client_socket, file_buffer):
    try:
        file_descriptor = open(upload_destination, "wb")
        file_descriptor.write(file_buffer)
        file_descriptor.close()
        client_socket.send("Successfully saved file to {}\r\n".format(upload_destination))
        return
    except:
        client_socket.send("Failed to save file to {}\r\n".format(upload_destination))
        return

def find_length(client_socket):
    data = recvall(client_socket, frame_struct.size)
    (msg_length,) = frame_struct.unpack(data)
    if not msg_length:
        return False
    return recvall(client_socket, msg_length)

def recvall(client_socket, length):
    data = []

    while length:
        datum = client_socket.recv(length)
        if not datum:
            raise EOFError("Socket closed due to no more bytes to receive.")
        length -= len(datum)
        data.append(datum)
    return ''.join(data)

def main():
    """
    Everything starts here
    """
    parse_cmd_line()

    if not listen:
        buffer = raw_input(">")

if __name__ == "__main__":
    parse_cmd_line()
    server_loop()

