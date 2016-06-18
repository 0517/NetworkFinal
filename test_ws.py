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


def recv_data(num, con):
    try:
        all_data = con.recv(num)
        if not len(all_data):
            return False
    except:
        return False
    # else:
    #     code_len = ord(all_data[1]) & 127
    # if code_len == 126:
    #     masks = all_data[4:8]
    #     data = all_data[8:]
    # elif code_len == 127:
    #     masks = all_data[10:14]
    #     data = all_data[14:]
    # else:
    #     masks = all_data[2:6]
    #     data = all_data[6:]
    # raw_str = ""
    # i = 0
    # for d in data:
    #     raw_str += chr(ord(d) ^ ord(masks[i % 4]))
    # i += 1
    print ord(all_data)
    # return chr(all_data)
    # data_length = con.recv(1)
    # data_lengths = struct.unpack("B", data_length)
    # data_length = data_lengths[0]&0b01111111
    # masking = data_lengths[0] >> 7
    # if data_length <= 125:
    #     payloadLength = data_length
    # elif data_length==126:
    #     payloadLength = struct.unpack("H", con.recv(2))[0]
    # elif data_length==127:
    #     payloadLength = struct.unpack("Q", con.recv(8))[0]
    # print "字符串长度是:%d"%(data_length,)
    # if masking==1:
    #     maskingKey = con.recv(4)
    #     maskingKey = maskingKey
    # data = con.recv(payloadLength)
    # if masking==1:
    #     i = 0
    #     true_data = ''
    #     for d in data:
    #         true_data += chr(ord(d) ^ ord(maskingKey[i % 4]))
    #         i += 1
    #     print true_data
    # else:
    #     print data
g_code_length = 0
g_header_length = 0

def get_datalength(msg):
    global g_code_length
    global g_header_length

    # print (len(msg))
    g_code_length = ord(msg[1]) & 127
    received_length = 0
    if g_code_length == 126:
        #g_code_length = msg[2:4]
        #g_code_length = (ord(msg[2])<<8) + (ord(msg[3]))
        g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
        g_header_length = 8
    elif g_code_length == 127:
        #g_code_length = msg[2:10]
        g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
        g_header_length = 14
    else:
        g_header_length = 6
    g_code_length = int(g_code_length)
    return g_code_length


def parse_data(msg):
    global g_code_length
    g_code_length = ord(msg[1]) & 127

    if g_code_length == 126:
        g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
        masks = msg[4:8]
        data = msg[8:]
    elif g_code_length == 127:
        g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
        masks = msg[10:14]
        data = msg[14:]
    else:
        masks = msg[2:6]
        data = msg[6:]
    i = 0
    raw_str = ''

    for d in data:
        raw_str += chr(ord(d) ^ ord(masks[i%4]))
        i += 1

    # print (u"总长度是：%d" % int(g_code_length))
    return raw_str


def hex2dec(string_num):
    return str(int(string_num.upper(), 16))


def recv(conn):
    length_buffer = 0
    buffer = ""
    buffer_utf8 = ""
    global g_code_length
    global g_header_length
    mm = conn.recv(128)
    if len(mm) <= 0:
        return
    if g_code_length == 0:
        get_datalength(mm)
    #接受的长度
    length_buffer = length_buffer + len(mm)
    buffer = buffer + mm
    if length_buffer - g_header_length < g_code_length:
        return
    else :
        buffer_utf8 = parse_data(buffer) #utf8
        msg_unicode = str(buffer_utf8).decode('utf-8', 'ignore') #unicode
        # print "receive", msg_unicode
        g_code_length = 0
        return msg_unicode
        # if msg_unicode=='quit':
        #     print (u'Socket%s Logout!' % (index))
        #     nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
        #     sendMessage(u'%s %s say: %s' % (nowTime, self.remote, self.name+' Logout'))
        #     deleteconnection(str(self.index))
        #     self.conn.close()
        #     break #退出线程
        # else:
        #     #print (u'Socket%s Got msg:%s from %s!' % (self.index, msg_unicode, self.remote))
        #     nowTime = time.strftime(u'%H:%M:%S',time.localtime(time.time()))
        #     sendMessage(u'%s %s say: %s' % (nowTime, self.remote, msg_unicode))
        #重置buffer和bufferlength



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

    send("hello world", con)
    while True:
        recvd = recv(con)
        print "receive", recvd
        send(recvd, con)
    # while True:
    #     message = con.recv(1024)
    #     if repr(message) == '':
    #         print "客户端断开链接"
    #         return
    #     if not message:
    #         print "receive", message
    #         send(message, con)
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


def testwsme(s):
    from websocket import WebSocket
    ws = WebSocket(s, 1024)
    ws.send("Hello world")
    while True:
        recvd = ws.recv()
        print "receive", recvd
        ws.send(recvd)

def start():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 9876))
    s.listen(1)
    while 1:
        t, _ = s.accept()
        threading.Thread(target=testwsme, args=(t,)).start()

if __name__ == '__main__':
    # new_service()
    start()