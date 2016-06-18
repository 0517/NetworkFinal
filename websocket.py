# _*_ coding:utf-8 _*_
import base64
import hashlib
import struct
import socket

__author__ = 'bohaohan'

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n" \
      "Upgrade: Websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "WebSocket-Origin: http://localhost:8888\r\n" \
      "Sec-WebSocket-Accept: {1}\r\n" \
      "WebSocket-Location: ws://{2}/\r\n" \
      "WebSocket-Protocol:sample\r\n\r\n"
f = open("test.jpg", "wb+")


class WebSocket():

    def __init__(self, socket, buffer_size=1024):
        self.socket = socket
        self.is_hand_shake = False
        self.buffer_size = buffer_size
        self.g_code_length = 0
        self.g_header_length = 0
        self.handshake()
        self.isData = False

    def send(self, data):

        if data and not self.isData:
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

        # struct 为 Python中处理二进制数的模块，二进制流为C，或网络流的形式。

        data = '%s%s' % (token, data)
        self.socket.send(data)

        return True

    def handshake(self):
        headers = {}
        shake = self.socket.recv(1024)
        print shake
        if not len(shake):
            return False

        header, data = shake.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, val = line.split(': ', 1)
            headers[key] = val

        if 'Sec-WebSocket-Key' not in headers:
            print ('This socket is not websocket, client close.')
            self.socket.close()
            return False

        sec_key = headers['Sec-WebSocket-Key']
        res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

        str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', 'localhost' + ':' + str('9876'))
        print str_handshake
        self.socket.send(str_handshake)
        print "hand shake success"
        self.is_hand_shake = True

        return True

    def recv(self, buffer_size=1024):

        length_buffer = 0
        buffer = ""
        buffer_utf8 = ""
        mm = self.socket.recv(buffer_size)

        if len(mm) <= 0:
            return
        if self.g_code_length == 0:
            self.get_datalength(mm)
        # 接受的长度
        length_buffer += len(mm)

        buffer = buffer + mm
        if length_buffer - self.g_header_length < self.g_code_length:
            return
        else:
            buffer_utf8 = self.parse_data(buffer)  # utf8
            print buffer_utf8
            if not self.isData:
                msg_unicode = str(buffer_utf8).decode('utf-8', 'ignore')  # unicode
            else:
                msg_unicode = bytes(buffer_utf8)
                f.write(msg_unicode)
            self.g_code_length = 0
            return msg_unicode

    def get_datalength(self, msg):

        self.g_code_length = ord(msg[1]) & 127

        if self.g_code_length == 126:
            self.g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
            self.g_header_length = 8

        elif self.g_code_length == 127:
            self.g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
            self.g_header_length = 14

        else:
            self.g_header_length = 6

        self.g_code_length = int(self.g_code_length)
        return self.g_code_length

    def parse_data(self, msg):

        self.g_code_length = ord(msg[1]) & 127

        if self.g_code_length == 126:
            self.g_code_length = struct.unpack('>H', str(msg[2:4]))[0]
            masks = msg[4:8]
            data = msg[8:]

        elif self.g_code_length == 127:
            self.g_code_length = struct.unpack('>Q', str(msg[2:10]))[0]
            masks = msg[10:14]
            data = msg[14:]

        else:
            masks = msg[2:6]
            data = msg[6:]

        i = 0
        raw_str = ''

        for d in data:
            if not self.isData:
                raw_str += chr(ord(d) ^ ord(masks[i % 4]))
            else:
                print d
                raw_str += ord(d) ^ ord(masks[i % 4])
            i += 1

        print (u"总长度是：%d" % int(self.g_code_length))
        return raw_str

    def close(self):
        self.socket.close()

    def setblocking(self, bo):
        self.socket.setblocking(bo)

if __name__ == '__main__':
    pass