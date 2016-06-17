# -*- coding: utf-8 -*-

import socket
import os
import threading
import time

__author__ = 'qm'


class DataSocket(threading.Thread):

    def __init__(self, server):
        super(DataSocket, self).__init__()
        self.daemon = True
        self.server = server
        self.listenSock = server.dataListenSock

    def run(self):
        # self.listenSock.settimeout(3)
        while True:
            try:
                data_sock, client_addr = self.listenSock.accept()
                print 'receive data socket from', client_addr
            except socket.timeout:
                pass
            except socket.error:
                break
            else:
                if self.server.dataSock is not None:
                    self.server.dataSock.close()
                    self.server.dataSock = data_sock
                    # print 1
                else:
                    self.server.dataSock = data_sock
                    # print data_sock
                    # print 2


class Server(threading.Thread):

    def __init__(self, controlSock, clientAddr):
        super(Server, self).__init__()
        self.daemon = True
        self.bufSize = 1024
        self.controlSock = controlSock
        self.clientAddr = clientAddr
        self.dataListenSock = None
        self.dataSock = None
        self.dataAddr = '127.0.0.1'
        self.dataPort = None
        self.username = ''
        self.authenticated = False
        self.cwd = os.getcwd()
        self.typeMode = 'Binary'
        self.dataMode = 'PORT'

    def run(self):
        self.controlSock.send(b'220 Service ready for new user.\r\n')
        while True:
            cmd = self.controlSock.recv(self.bufSize)
            if cmd == '':
                self.controlSock.close()
                break
            cmdHead = cmd.split()[0].upper()
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
                        self.controlSock.send(b'230 User logged in, proceed.\r\n')
                        self.authenticated = True
            elif cmdHead == 'PWD':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                else:
                    self.controlSock.send('257 "%s" is the current directory.\r\n' % self.cwd)
            elif cmdHead == 'CWD':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                elif len(cmd.split()) < 2:
                    self.controlSock.send('250 "%s" is the current directory.\r\n' % self.cwd)
                else:
                    # programDir = os.getcwd()
                    os.chdir(self.cwd)
                    nextDir = cmd.split()[1]
                    try:
                        os.chdir(nextDir)
                    except OSError as e:
                        print e
                        self.controlSock.send(b'550 Requested action not taken. File unavailable (e.g., file busy).\r\n')
                    else:
                        self.cwd = os.getcwd()
                        self.controlSock.send('250 "%s" is the current directory.\r\n' % self.cwd)
                    # os.chdir(programDir) 为什么要再变回去???
            # elif cmd == 'TYPE':
            #     if not self.authenticated:
            #         self.controlSock.send(b'530 Not logged in.\r\n')
            #     elif len(cmd.split() < 2):
            #         self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
            #     elif cmd.split()[1] == 'I':
            #         self.typeMode = 'Binary'
            #     else:
            #         self.controlSock.send(b'504 Command not implemented for that parameter.\r\n')
            elif cmdHead == 'PASV':
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                else:
                    # if self.dataListenSock is not None:
                    # self.dataListenSock.close()
                    if self.dataListenSock is None:
                        self.dataListenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.dataListenSock.bind((self.dataAddr, 0))
                        self.dataPort = self.dataListenSock.getsockname()[1]
                        print self.dataAddr, self.dataPort
                        self.dataListenSock.listen(5)
                        self.dataMode = 'PASV'
                        DataSocket(self).start()
                        # 为什么
                        self.controlSock.send('227 Entering passive mode (%s,%s)\r\n' % (self.dataAddr, self.dataPort))
            elif cmdHead == 'NLST':
                time.sleep(0.5)
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                elif self.dataMode == 'PASV' and self.dataSock is not None:
                    self.controlSock.send(b'125 Data connection already open. Transfer starting.\r\n')
                    directory = '\r\n'.join(os.listdir(self.cwd)) + "\r\n"
                    self.dataSock.send(directory)
                    self.dataSock = None
                    self.controlSock.send(b'225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                else:
                    self.controlSock.send(b"425 Can't open data connection.\r\n")
            elif cmdHead == 'RETR':
                time.sleep(0.5)
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
                elif self.dataMode == 'PASV' and self.dataSock is not None:
                    # programDir = os.getcwd()
                    # os.chdir(self.cwd)
                    self.controlSock.send(b'125 Data connection already open; transfer starting.\r\n')
                    file_name = cmd.split()[1]
                    try:
                        self.dataSock.send(open(file_name, 'rb').read())
                    except Exception as e:
                        print e
                        # 没有文件的话在此处理
                        self.controlSock.send(b'550 Requested action not taken. File unavailable (e.g., file busy).\r\n')
                    self.dataSock.close()
                    self.dataSock = None
                    self.controlSock.send(b'225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                else:
                    self.controlSock.send(b"425 Can't open data connection.\r\n")
            elif cmdHead == 'STOR':
                time.sleep(0.5)
                if not self.authenticated:
                    self.controlSock.send(b'530 Not logged in.\r\n')
                elif len(cmd.split()) < 2:
                    self.controlSock.send(b'501 Syntax error in parameters or arguments.\r\n')
                elif self.dataMode == 'PASV' and self.dataSock is not None:
                    # programDir = os.getcwd()
                    # os.chdir(self.cwd)
                    self.controlSock.send(b'125 Data connection already open; transfer starting.\r\n')
                    file_name = open(cmd.split()[1], 'w')
                    # 在非阻塞模式下, 如果recv()调用没有发现任何数据或者send()调用无法立即发送数据, 那么将引发socket.error异常。在阻塞模式下, 这些调用在处理之前都将被阻塞。
                    self.dataSock.setblocking(False)
                    while True:
                        try:
                            data = self.dataSock.recv(self.bufSize)
                            if data == b'':
                                break
                            file_name.write(data)
                        except socket.error:
                            break
                    file_name.close()
                    print "success"
                    self.dataSock.close()
                    self.dataSock = None
                    self.controlSock.send(b'225 Closing data connection. Requested file action successful (for example, file transfer or file abort).\r\n')
                else:
                    self.controlSock.send(b"425 Can't open data connection.\r\n")


if __name__ == '__main__':
    listenAddr = "127.0.0.1"
    listenPort = 12344
    listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenSock.bind((listenAddr, listenPort))
    listenSock.listen(5)
    while True:
        controlSock, clientAddr = listenSock.accept()
        Server(controlSock, clientAddr).start()
