#!/usr/bin/env python2.7

import sys, struct, socket, argparse, threading, subprocess

file_buffer = ""
listen = ""
cmd = ""
upload = True
execute = ""
target = ""
upload_destination = "/home/ubuntu/test.txt"

frame_struct = struct.Struct("!I")

def put_chunk(sock, msg):
    """
    pt.1 of network protocol
    simple protocol for sending based on chunks.
    checks len of msg to send, packs in binary struct,
    sends this, then the msg, then a packed 
    binary struct of len 0 to tell server sending
    is over and it's ok to reply
    """
    chunk_length = len(msg)
    sock.send(frame_struct.pack(chunk_length))
    sock.send(msg)
    sock.send(frame_struct.pack(len(""))) 
    return

def get_chunk(sock):
    """
    pt.2 of network protocol
    calls recvall to recv bytes in the socket,
    unpacks any struct objs to get len of msg and has
    recvall then recv actual msg in socket.

    """
    data = recvall(sock, frame_struct.size)
    (msg_length,) = frame_struct.unpack(data)
    if not msg_length:
        return False
    return recvall(sock, msg_length)

def recvall(sock, length):
    """
    pt.3 of network protocol
    calls recv on socket and appends the
    received struct obj or msg data to
    list to be returned
    """
    data = []
    while length:
        chunk = sock.recv(length)
        if not chunk:
            raise EOFError("Socket closed due to no more bytes to receive.")
        length -= len(chunk)
        data.append(chunk)
    return ''.join(data)

def client_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target[0], target[1]))
        print "Connected to: {} on port: {}".format(client.getpeername()[0],
                                                    client.getpeername()[1])
        try:
            while True:
                recv_buffer = ""
                msg = raw_input(">")
                if msg == "exit":
                    client.close()
                    sys.exit(0)
                put_chunk(client, msg)

                while True:
                    data = get_chunk(client)
                    if not data:
                        print recv_buffer
                        break
                    else:
                        recv_buffer += data
        except EOFError:
            print "Socket has closed."
        finally:
            print "Closing in inner client try/except"
            client.close()
    except socket.gaierror:
        print "Name or service not known."
    except socket.error as e:
        print e

def server_loop():
    global target

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((target[0], target[1]))
    server.listen(2)

    while True:
        print "waiting for client to connect..."
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()
        print "spun off new client thread..."

def run_cmd(cmd):
    pass

def client_handler(client_socket):
    global upload
    global execute
    global cmd

    """
    If -u is chosen on target, will receive bytes
    and try to write them out to file.
    """
    if upload:
        file_buffer = ""

        try:
            while True:
                data = get_chunk(client_socket)
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
        print "Sending msg to client now..."
        msg = "Successfully saved file to {}\r\n".format(upload_destination)
        put_chunk(client_socket, msg)
        return
    except:
        print "sending msg to client now..."
        msg = "Failed to save file to {}\r\n".format(upload_destination)
        put_chunk(client_socket, msg)
        return

def main():
    parse_cmd_line()

    if not listen:
        buffer = raw_input(">")

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

ascii_art = {"greet": r'''
             *     ,MMM8&&&.            *
                  MMMMM8&&&&&    .
                 MMMM88&&&&&&&
     *           MMM PyCat &&&
                 MMM88&&&&&&&&
                 'MMM88&&&&&&'
                   'MMM8&&&'      *
          |\___/|
          )     (             .              '
         =\     /=
           )===(       *
          /     \
          |     |
         /       \
         \       /
  _/\_/\_/\__  _/_/\_/\_/\_/\_/\_/\_/\_/\_/\_
  |  |  |  |( (  |  |  |  |  |  |  |  |  |  |
  |  |  |  | ) ) |  |  |  |  |  |  |  |  |  |
  |  |  |  |(_(  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  '''}

if __name__ == "__main__":
    print ascii_art["greet"]
    parse_cmd_line()
    if listen:
        server_loop()
    else:
        client_sender()


