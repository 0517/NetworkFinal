# _*_ coding:utf-8 _*_
import base64
import hashlib
import struct
import socket
from log.log import LoggingManagement

__author__ = 'bohaohan'

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HANDSHAKE_STRING = "HTTP/1.1 101 Web Socket Protocol Handshake\r\n" \
      "Upgrade: Websocket\r\n" \
      "Connection: Upgrade\r\n" \
      "WebSocket-Origin: http://localhost:8888\r\n" \
      "Sec-WebSocket-Accept: {1}\r\n" \
      "WebSocket-Location: ws://{2}/\r\n" \
      "WebSocket-Protocol:sample\r\n\r\n"

log = LoggingManagement()

class WebSocket:

    def __init__(self, socket, buffer_size=1024):
        self.socket = socket
        self.is_hand_shake = False
        self.buffer_size = buffer_size
        self.g_code_length = 0
        self.g_header_length = 0
        self.handshake()
        self.isData = False
        self.opCode = 1

    def send(self, data, opcode=1):

        if data:
            data = str(data)
        else:
            return False

        if opcode == 1:
            token = "\x81"
        else:
            token = "\x82"

        length = len(data)

        if length < 126:
            token += struct.pack("B", length)
        elif length <= 0xFFFF:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)

        data = '%s%s' % (token, data)
        self.socket.send(data)

        return True

    def handshake(self):
        headers = {}
        shake = self.socket.recv(1024)
        log.DEBUG(shake)
        if not len(shake):
            return False

        header, data = shake.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, val = line.split(': ', 1)
            headers[key] = val

        if 'Sec-WebSocket-Key' not in headers:
            log.INFO('This socket may be not websocket, client close.')
            self.socket.close()
            return False

        sec_key = headers['Sec-WebSocket-Key']
        res_key = base64.b64encode(hashlib.sha1(sec_key + MAGIC_STRING).digest())

        str_handshake = HANDSHAKE_STRING.replace('{1}', res_key).replace('{2}', 'localhost' + ':' + str('9876'))
        log.DEBUG(str_handshake)
        self.socket.send(str_handshake)
        log.DEBUG("hand shake success")
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
        if False:
            return
        else:
            buffer_utf8 = self.parse_data(buffer)  # utf8

            if self.opCode == 1:
                msg_unicode = str(buffer_utf8).decode('utf-8', 'ignore')  # unicode
            else:
                msg_unicode = bytes(buffer_utf8)

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

        if ord(msg[0]) == 130:
            self.opCode = 2

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

            raw_str += chr(ord(d) ^ ord(masks[i % 4]))
            i += 1
        log.DEBUG(u"总长度是：%d" % int(self.g_code_length))
        return raw_str

    def close(self):
        self.socket.close()

    def setblocking(self, bo):
        self.socket.setblocking(bo)

if __name__ == '__main__':
    pass
