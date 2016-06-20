# -*- coding: utf-8 -*-

__author__ = 'qm'


import socket
import os
import threading
import time
from websocket import WebSocket
import shutil
import json
from ip_management import IpListManagement
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


class DataSocket(threading.Thread):

    def __init__(self, server):
        super(DataSocket, self).__init__()
        self.daemon = True
        self.server = server
        self.listenSock = server.dataListenSock

    def run(self):
        while True:
            try:
                data_sock, client_addr = self.listenSock.accept()
                if not self.server.ifPrimitive:
                    data_sock = WebSocket(data_sock)
                    data_sock.isData = True
                print 'receive data socket from', client_addr
            except socket.timeout:
                pass
            except socket.error:
                break
            else:
                if self.server.data_socket_for == 'NLST':
                    if self.server.nlst_data_socket is not None:
                        self.server.nlst_data_socket.close()
                        self.server.nlst_data_socket = data_sock
                    else:
                        self.server.nlst_data_socket = data_sock
                elif self.server.data_socket_for == 'RETR':
                    if self.server.retr_data_socket is not None:
                        self.server.retr_data_socket.close()
                        self.server.retr_data_socket = data_sock
                    else:
                        self.server.retr_data_socket = data_sock
                elif self.server.ip_sokcet_for == 'IP':
                    if self.server.ip_data_socket is not None:
                        self.server.ip_data_socket.close()
                        self.server.ip_data_socket = data_sock
                    else:
                        self.server.ip_data_socket = data_sock
                else:
                    if self.server.stor_data_socket is not None:
                        self.server.stor_data_socket.close()
                        self.server.stor_data_socket = data_sock
                    else:
                        self.server.stor_data_socket = data_sock

                # if self.server.dataSock is not None:
                #     self.server.dataSock.close()
                #     self.server.dataSock = data_sock
                # else:
                #     self.server.dataSock = data_sock


class Server(threading.Thread):

    def __init__(self, controlSock, clientAddr, ifPrimitive, root, ip_management):

        super(Server, self).__init__()
        self.daemon = True
        self.bufSize = 2000000000
        self.ifPrimitive = ifPrimitive
        if ifPrimitive:
            self.controlSock = controlSock
        else:
            self.controlSock = WebSocket(controlSock, self.bufSize)
        self.clientAddr = clientAddr
        self.dataListenSock = None
        # self.dataSock = None
        self.dataAddr = '127.0.0.1'
        self.dataPort = None
        self.username = ''
        self.authenticated = False
        self.if_administrator = False
        self.cwd = root
        self.root_wd = root
        self.typeMode = 'Binary'
        self.dataMode = 'PORT'
        self.nlst_data_socket = None
        self.retr_data_socket = None
        self.stor_data_socket = None
        self.ip_data_socket = None
        self.data_socket_for = 'NLST'
        self.ip_management = ip_management

    def run(self):

        self.controlSock.send(b'220 Service ready for new user.\r\n')

        while True:

            cmd = self.controlSock.recv(self.bufSize)

            if cmd == '':
                self.controlSock.close()
                break

            cmdHead = cmd.split()[0].upper()
            print 'receive head', cmdHead
            if cmdHead == 'QUIT':
                self.controlSock.send(b'221 Service closing control connection.\r\n')
                self.controlSock.close()
                break

            elif cmdHead == 'HELP':
                self.controlSock.send(b'214 QUIT HELP USER PASS PWD CWD TYPE PASV NLST RETR STOR\r\n')

            elif cmdHead == 'USER':

                if len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                else:
                    self.username = cmd.split()[1]
                    self.controlSock.send(b'331 User name okay, need password.\r\n')

            elif cmdHead == 'PASS':

                if self.username == '':
                    self.controlSock.send(b'503 Bad sequence of commands.\r\n')

                else:

                    if len(cmd.split()) < 2:
                        self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                    else:
                        if self.username == 'administrator' and cmd.split()[1] == 'administrator':
                            self.if_administrator = True
                        self.controlSock.send(b'230 User logged in, proceed.\r\n')
                        self.authenticated = True

            elif cmdHead == 'PWD':

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                else:
                    self.controlSock.send('257 "%s" is the current directory.\r\n' % self.cwd)

            elif cmdHead == 'CDUP':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                else:
                    try:
                        os.chdir("..")
                    except OSError as e:
                        print e
                        self.controlSock.send(b'550 Requested action not taken. File unavailable (e.g., file busy).\r\n')
                    else:
                        self.cwd = os.getcwd()
                        self.controlSock.send('250 "%s" is the current directory.\r\n' % self.cwd)
                        os.chdir(self.root_wd)

            elif cmdHead == 'RMD':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
                else:
                    rm_dir = cmd.split()[1]
                    os.chdir(self.cwd)
                    try:
                        shutil.rmtree(rm_dir)
                    except Exception as e:
                        print e
                        self.controlSock.send('550 Requested action not taken.')
                    else:
                        self.controlSock.send('250 Requested file action okay, completed.')
                    os.chdir(self.root_wd)

            elif cmdHead == 'MKD':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
                else:
                    new_dir = cmd.split()[1]
                    os.chdir(self.cwd)
                    try:
                        os.mkdir(new_dir)
                    except Exception as e:
                        print e
                        self.controlSock.send('550 Requested action not taken.')
                    else:
                        self.controlSock.send('250 Requested file action okay, completed.')
                    os.chdir(self.root_wd)

            elif cmdHead == 'DELETE':

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
                else:
                    os.chdir(self.cwd)
                    delete_dir = cmd.split()[1]
                    try:
                        os.remove(delete_dir)
                    except Exception as e:
                        print e
                        self.controlSock.send('550 Requested action not taken.')
                    else:
                        self.controlSock.send('250 Requested file action okay, completed.')
                    os.chdir(self.root_wd)

            elif cmdHead == 'CWD':

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send('250 "%s" is the current directory.\r\n' % self.cwd)

                else:
                    print "change to dir:", cmd.split()[1]
                    os.chdir(self.cwd)
                    next_dir = cmd.split()[1]
                    try:
                        os.chdir(next_dir)
                    except OSError as e:
                        print e
                        self.controlSock.send(b'550 Requested action not taken. File unavailable (e.g., file busy).\r\n')

                    else:
                        self.cwd = os.getcwd()
                        self.controlSock.send('250 "%s" is the current directory.\r\n' % self.cwd)
                    os.chdir(self.root_wd)

            elif cmd == 'TYPE':

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                else:
                    self.controlSock.send("502 Command not implemented\r\n")

            elif cmdHead == 'PASV':

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                elif cmd.split()[1] != 'NLST' and cmd.split()[1] != 'RETR' and cmd.split()[1] != 'STOR' and cmd.split()[1] != 'IP':
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                else:
                    if self.dataListenSock is None:
                        self.dataListenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.dataListenSock.bind((self.dataAddr, 0))
                        self.dataPort = self.dataListenSock.getsockname()[1]
                        print self.dataAddr, self.dataPort
                        self.dataListenSock.listen(5)
                        self.dataMode = 'PASV'
                        DataSocket(self).start()
                        # 为什么
                    self.data_socket_for = cmd.split()[1]
                    self.controlSock.send('227 Entering passive mode (%s,%s)\r\n' % (self.dataAddr, self.dataPort))

            elif cmdHead == 'PORT':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                else:
                    self.controlSock.send("502 Command not implemented\r\n")

            elif cmdHead == 'NLST':

                time.sleep(0.5)

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif self.dataMode == 'PASV' and self.nlst_data_socket is not None:
                    self.controlSock.send(b'125 Data connection already open. Transfer starting.\r\n')
                    os.chdir(self.cwd)
                    dir_list = os.listdir(self.cwd)
                    dir_with_type = {'dir': [], 'file': []}
                    for ob in dir_list:
                        if ob[0] == '.':
                            continue
                        if os.path.isdir(ob):
                            dir_with_type['dir'].append(ob)
                        else:
                            dir_with_type['file'].append(ob)
                    directory = json.dumps(dir_with_type)
                    self.nlst_data_socket.send(directory)
                    self.nlst_data_socket.close()
                    self.nlst_data_socket = None
                    self.controlSock.send(b'225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                    os.chdir(self.root_wd)
                else:
                    self.controlSock.send(b"425 Can't open data connection.\r\n")

            elif cmdHead == 'RETR':

                time.sleep(0.5)

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                elif self.dataMode == 'PASV' and self.retr_data_socket is not None:
                    self.controlSock.send(b'125 Data connection already open; transfer starting.\r\n')
                    file_name = cmd.split()[1]

                    try:
                        os.chdir(self.cwd)
                        self.retr_data_socket.send(open(file_name, 'rb').read(), opcode=2)
                    except Exception as e:
                        print e
                        # 没有文件的话在此处理
                        self.controlSock.send(b'550 Requested action not taken. File unavailable (e.g., file busy).\r\n')
                    else:
                        self.controlSock.send(b'225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                    os.chdir(self.root_wd)
                    self.retr_data_socket.close()
                    self.retr_data_socket = None
                else:
                    self.controlSock.send(b"425 Can't open data connection.\r\n")

            elif cmdHead == 'STOR':

                time.sleep(0.5)

                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')

                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')

                elif self.dataMode == 'PASV' and self.stor_data_socket is not None:
                    self.controlSock.send(b'125 Data connection already open; transfer starting.\r\n')
                    os.chdir(self.cwd)
                    file_name = cmd[cmd.index(' ')+1:]
                    f = open(file_name, 'ab+')
                    # 在非阻塞模式下, 如果recv()调用没有发现任何数据或者send()调用无法立即发送数据, 那么将引发socket.error异常。在阻塞模式下, 这些调用在处理之前都将被阻塞。
                    self.stor_data_socket.setblocking(False)
                    while True:
                        try:
                            data = self.stor_data_socket.recv(self.bufSize)
                            if data == b'':
                                break
                            if data is None:
                                continue
                            f.write(data)
                        except socket.error:
                            break
                    f.close()
                    print "success"
                    self.stor_data_socket.close()
                    self.stor_data_socket = None
                    self.controlSock.send('225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                    os.chdir(self.root_wd)
                else:
                    self.controlSock.send("425 Can't open data connection.\r\n")

            elif cmdHead == 'IP':
                if self.if_administrator:
                    if len(cmd.split()) < 2 and self.ip_data_socket is not None and self.dataMode == 'PASV':
                        try:
                            self.ip_data_socket.send(json.dumps(self.ip_management.ip_data['ip_list']))
                        except Exception as e:
                            self.controlSock.send('550 Requested action not taken.')
                        else:
                            self.controlSock.send('225 Closing data connection. Requested action successful.\r\n')
                        self.ip_data_socket.close()
                        self.ip_data_socket = None
                    elif cmd.split()[1] == 'ADD':
                        address = cmd.split()[2]
                        if self.ip_management.add_ip(address):
                            self.controlSock.send('250 Requested action okay, completed')
                        else:
                            self.controlSock.send('550 Requested action not taken.')
                    elif cmd.split()[1] == 'DELETE':
                        id = cmd.split()[2]
                        if self.ip_management.delete_ip(id):
                            self.controlSock.send('250 Requested action okay, completed')
                        else:
                            self.controlSock.send('550 Requested action not taken.')
                    elif cmd.split()[1] == 'UPDATE':
                        id = cmd.split()[2]
                        address = cmd.split()[3]
                        if self.ip_management.modify_ip(id, address):
                            self.controlSock.send('250 Requested action okay, completed')
                        else:
                            self.controlSock.send('550 Requested action not taken.')
                    else:
                        self.controlSock.send('501 Syntax error in parameters or arguments.\r\n')
                else:
                    # 非管理员
                    self.controlSock.send('534 Unable to take action\r\n')


class FTPServer(threading.Thread):

    def __init__(self, client_type, ip_management):
        super(FTPServer, self).__init__()
        self.WebPort = 12344
        self.PrimitivePort = 12345
        self.listenAddress = '127.0.0.1'
        self.client_type = client_type
        self.ip_management = ip_management

    def run(self):
        if self.client_type == 'Primitive':
            primitiveScoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            primitiveScoket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            primitiveScoket.bind((self.listenAddress, self.PrimitivePort))
            primitiveScoket.listen(5)

            while True:
                controlSock, clientAddr = primitiveScoket.accept()
                for i in self.ip_management.ip_data['ip_list']:
                    if clientAddr[0] == i['address']:
                        controlSock.send('421 Service not available, closing control connection')
                        controlSock.close()
                Server(controlSock, clientAddr, True, os.getcwd(), self.ip_management).start()

        else:
            webScoket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            webScoket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            webScoket.bind((self.listenAddress, self.WebPort))
            webScoket.listen(5)

            while True:
                controlSock, clientAddr = webScoket.accept()
                for i in self.ip_management.ip_data['ip_list']:
                    if clientAddr[0] == i['address']:
                        controlSock.send('421 Service not available, closing control connection')
                        controlSock.close()
                Server(controlSock, clientAddr, False, os.getcwd(), self.ip_management).start()

if __name__ == '__main__':
    ip_management = IpListManagement()
    FTPServer('Primitive', ip_management).start()
    FTPServer('Web', ip_management).start()

