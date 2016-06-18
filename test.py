# -*- coding: utf-8 -*-

__author__ = 'qm'


import socket
import threading
import sys
import base64
import hashlib
import struct

# ====== config ======
HOST = 'localhost'
PORT = 3368
MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Switching Protocols\r\n" \
"Upgrade:websocket\r\n" \
"Connection: Upgrade\r\n" \
"Sec-WebSocket-Accept: {1}\r\n" \
"WebSocket-Location: ws://{2}/chat\r\n" \
"WebSocket-Protocol:chat\r\n\r\n"


def recv_data(input_data):
    code_len = ord(input_data[1]) & 127
    if code_len == 126:
        masks = input_data[4:8]
        data = input_data[8:]
    elif code_len == 127:
        masks = input_data[10:14]
        data = input_data[14:]
    else:
        masks = input_data[2:6]
        data = input_data[6:]
    raw_str = ""
    i = 0
    for d in data:
        raw_str += chr(ord(d) ^ ord(masks[i % 4]))
        i += 1
    return raw_str


# send data
def send_data(output_data):
    if output_data:
        data = str(output_data)
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
    # struct为Python中处理二进制数的模块，二进制流为C，或网络流的形式。
    data = '%s%s' % (token, data)
    return data


# handshake
def handshake(recv_data):
    headers = {}
    shake = recv_data

    if not len(shake):
        return False

    header, data = shake.split('\r\n\r\n', 1)
    for line in header.split('\r\n')[1:]:
        key, val = line.split(': ', 1)
        headers[key] = val

    if 'Sec-WebSocket-Key' not in headers:
        print ('This socket is not websocket, client close.')
        return False

    sec_key = headers['Sec-WebSocket-Key']
    res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

    str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', HOST + ':' + str(PORT))
    print str_handshake
    return str_handshake


def new_service():
    """start a service socket and listen
    when coms a connection, start a new thread to handle it"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 3368))
    sock.listen(5)

    while True:
        connection, address = sock.accept()
        print "Got connection from ", address
        try:
            shake_return = handshake(connection.recv(1024))
            connection.send(shake_return)
        except Exception as e:
            print e
        while True:
            try:
                recv = connection.recv(1024)
                print recv
                connection.send(send_data(recv))
            except Exception as e:
                print e
                connection.close()

if __name__ == '__main__':
    # new_service()
    f = open('testsend.jpg', 'rb').read()
    print type(f)


# coding=utf8
# !/usr/bin/python


# import struct,socket
# import hashlib
# import threading,random
# import time
# import struct
# from base64 import b64encode, b64decode
#
#
# connectionlist = {}
# g_code_length = 0
# g_header_length = 0
#
#
# def hex2dec(string_num):
#     return str(int(string_num.upper(), 16))
#
#
#
#
# def get_datalength(msg):
#     global g_code_length
#     global g_header_length
#
#     print (len(msg))
#     g_code_length = ord(msg[1]) & 127
#     received_length = 0
#     if g_code_length == 126:
#         # g_code_length = msg[2:4]
#         # g_code_length = (ord(msg[2])<<8) + (ord(msg[3]))
#         g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
#         g_header_length = 8
#     elif g_code_length == 127:
#         #g_code_length = msg[2:10]
#         g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
#         g_header_length = 14
#     else:
#         g_header_length = 6
#         g_code_length = int(g_code_length)
#     return g_code_length
#
#
# def parse_data(msg):
#     global g_code_length
#     g_code_length = ord(msg[1]) & 127
#     received_length = 0;
#     if g_code_length == 126:
#         g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
#         masks = msg[4:8]
#         data = msg[8:]
#     elif g_code_length == 127:
#         g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
#         masks = msg[10:14]
#         data = msg[14:]
#     else:
#         masks = msg[2:6]
#         data = msg[6:]
#     i = 0
#     raw_str = ''
#
#     for d in data:
#         raw_str += chr(ord(d) ^ ord(masks[i%4]))
#         i += 1
#
#     print (u"总长度是：%d" % int(g_code_length))
#     return raw_str
#
#
# def sendMessage(message):
#     global connectionlist
#
#     message_utf_8 = message.encode('utf-8')
#     for connection in connectionlist.values():
#         back_str = []
#         back_str.append('\x81')
#         data_length = len(message_utf_8)
#
#         if data_length <= 125:
#             back_str.append(chr(data_length))
#         elif data_length <= 65535 :
#             back_str.append(struct.pack('b', 126))
#             back_str.append(struct.pack('>h', data_length))
#
#         elif data_length <= (2^64-1):
#             back_str.append(struct.pack('b', 127))
#             back_str.append(struct.pack('>q', data_length))
#         else:
#             print (u'太长了')
#         msg = ''
#         for c in back_str:
#             msg += c
#             back_str = str(msg) + message_utf_8
#
#         if back_str != None and len(back_str) > 0:
#             print (back_str)
#             connection.send(back_str)
#
#
# def deleteconnection(item):
#     global connectionlist
#     del connectionlist['connection'+item]
#
#
# class WebSocket(threading.Thread):#继承Thread
#     GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
#
#     def __init__(self,conn,index,name,remote, path="/"):
#         threading.Thread.__init__(self)
#         self.conn = conn
#         self.index = index
#         self.name = name
#         self.remote = remote
#         self.path = path
#         self.buffer = ""
#         self.buffer_utf8 = ""
#         self.length_buffer = 0
#         self.handshaken = False
#
#     def run(self):
#         print('Socket%s Start!' % self.index)
#         headers = {}
#         while True:
#             if self.handshaken == False:
#                 print ('Socket%s Start Handshaken with %s!' % (self.index,self.remote))
#                 self.buffer += bytes.decode(self.conn.recv(1024))
#
#             if self.buffer.find('\r\n\r\n') != -1:
#                 header, data = self.buffer.split('\r\n\r\n', 1)
#                 for line in header.split("\r\n")[1:]:
#                     key, value = line.split(": ", 1)
#                     headers[key] = value
#
#                 headers["Location"] = ("ws://%s%s" %(headers["Host"], self.path))
#                 key = headers['Sec-WebSocket-Key']
#                 token = b64encode(hashlib.sha1(str.encode(str(key + self.GUID))).digest())
#
#                 handshake="HTTP/1.1 101 Switching Protocols\r\n"\
#                     "Upgrade: websocket\r\n"\
#                     "Connection: Upgrade\r\n"\
#                     "Sec-WebSocket-Accept: "+bytes.decode(token)+"\r\n"\
#                     "WebSocket-Origin: "+str(headers["Origin"])+"\r\n"\
#                     "WebSocket-Location: "+str(headers["Location"])+"\r\n\r\n"
#
#                 self.conn.send(str.encode(str(handshake)))
#                 self.handshaken = True
#                 print ('Socket %s Handshaken with %s success!' %(self.index, self.remote))
#                 sendMessage(u'Welcome, ' + self.name + ' !')
#                 self.buffer_utf8 = ""
#                 g_code_length = 0
#
#
#       else:
#         global g_code_length
#         global g_header_length
#         mm=self.conn.recv(128)
#         if len(mm) <= 0:
#           continue
#         if g_code_length == 0:
#           get_datalength(mm)
#         #接受的长度
#         self.length_buffer = self.length_buffer + len(mm)
#         self.buffer = self.buffer + mm
#         if self.length_buffer - g_header_length < g_code_length :
#           continue
#         else :
#           self.buffer_utf8 = parse_data(self.buffer) #utf8
#           msg_unicode = str(self.buffer_utf8).decode('utf-8', 'ignore') #unicode
#           if msg_unicode=='quit':
#             print (u'Socket%s Logout!' % (self.index))
#             nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
#             sendMessage(u'%s %s say: %s' % (nowTime, self.remote, self.name+' Logout'))
#             deleteconnection(str(self.index))
#             self.conn.close()
#             break #退出线程
#           else:
#             #print (u'Socket%s Got msg:%s from %s!' % (self.index, msg_unicode, self.remote))
#             nowTime = time.strftime(u'%H:%M:%S',time.localtime(time.time()))
#             sendMessage(u'%s %s say: %s' % (nowTime, self.remote, msg_unicode))
#           #重置buffer和bufferlength
#           self.buffer_utf8 = ""
#           self.buffer = ""
#           g_code_length = 0
#           self.length_buffer = 0
#       self.buffer = ""
#
#
# class WebSocketServer(object):
#   def __init__(self):
#     self.socket = None
#   def begin(self):
#     print( 'WebSocketServer Start!')
#     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
#     self.socket.bind(("127.0.0.1",12345))
#     self.socket.listen(50)
#
#
#     global connectionlist
#
#
#     i=0
#     while True:
#       connection, address = self.socket.accept()
#
#
#       username=address[0]
#       newSocket = WebSocket(connection,i,username,address)
#       newSocket.start() #开始线程,执行run函数
#       connectionlist['connection'+str(i)]=connection
#       i = i + 1
#
#
# if __name__ == "__main__":
#   server = WebSocketServer()
#   server.begin()