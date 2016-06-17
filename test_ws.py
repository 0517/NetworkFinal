# __author__ = 'bohaohan'
# # _*_ coding:utf-8 _*_
# __author__ = 'Patrick'
#
import socket
import threading
import sys
import base64
import hashlib
import struct
#
# # ====== config ======
# HOST = 'localhost'
# PORT = 3368
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n" \
      "Upgrade: Websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "WebSocket-Origin: http://localhost:8888\r\n" \
      "Sec-WebSocket-Accept: {1}\r\n" \
      "WebSocket-Location: ws://{2}/\r\n" \
      "WebSocket-Protocol:sample\r\n\r\n"
#
#
class Th(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.con = connection

    def run(self):
        while True:
            pass
        self.con.close()

    def recv_data(self, num):
        try:
            all_data = self.con.recv(num)
            if not len(all_data):
                return False
        except:
            return False
        else:
            code_len = ord(all_data[1]) & 127
        if code_len == 126:
            masks = all_data[4:8]
            data = all_data[8:]
        elif code_len == 127:
            masks = all_data[10:14]
            data = all_data[14:]
        else:
            masks = all_data[2:6]
            data = all_data[6:]
        raw_str = ""
        i = 0
        for d in data:
            raw_str += chr(ord(d) ^ ord(masks[i % 4]))
        i += 1
        return raw_str

# send data
    def send_data(self, data):
        if data:
            data = str(data)
        else:
            return False
        token = "\x81"
        length = len(data)
        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        #struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
        data = '%s%s' % (token, data)
        self.con.send(data)
        return True
#
#


def send(data, socket):

    if data:
        data = str(data)
    else:
        return False
    token = "\x81"
    length = len(data)
    if length < 126:
        token += struct.pack("B", length)
    elif length <= 0xFFFF:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    #struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
    data = '%s%s' % (token, data)
    socket.send(data)
    return True


# handshake
def handshake(con):
    headers = {}
    shake = con.recv(1024)
    print shake
    if not len(shake):
        return False

    header, data = shake.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, val = line.split(': ', 1)
        headers[key] = val

    if 'Sec-WebSocket-Key' not in headers:
        print ('This socket is not websocket, client close.')
        con.close()
        return False

    sec_key = headers['Sec-WebSocket-Key']
    res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

    str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', 'localhost' + ':' + str('9876'))
    print str_handshake
    con.send(str_handshake)

    # send("hello world", con)
    # con.send("hello world")

    return True


def new_service():
    """start a service socket and listen
    when coms a connection, start a new thread to handle it"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', 3368))
        sock.listen(1000)
        #链接队列大小
        print "bind 3368,ready to use"
    except:
        print("Server is already running,quit")
        sys.exit()

    while True:
        connection, address = sock.accept()
        #返回元组（socket,add），accept调用时会进入waite状态
        print "Got connection from ", address
        if handshake(connection):
            print "handshake success"
            try:
                t = Th(connection)
                t.start()
                print 'new thread for client ...'
            except:
                print 'start new thread error'
                connection.close()


#!/usr/bin/env python
import socket
import threading
import time


def handle(s):
    print repr(s.recv(4096))
    s.send("""
    HTTP/1.1 101 Web Socket Protocol Handshake\r
    Upgrade: WebSocket\r
    Connection: Upgrade\r
    WebSocket-Origin: http://localhost:8888\r
    WebSocket-Location: ws://localhost:9876/\r
    WebSocket-Protocol: sample
    """.strip() + '\r\n\r\n')
    time.sleep(1)
    s.send('\x00hello\xff')
    time.sleep(1)
    s.send('\x00world\xff')
    s.close()


def start():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 9876))
    s.listen(1)
    while 1:
        t, _ = s.accept()
        threading.Thread(target=handshake, args=(t,)).start()

if __name__ == '__main__':
    # new_service()
    start()