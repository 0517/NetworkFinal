import socket
import re
import time


class FTPClient:

    def __init__(self):
        self.controlSock = None
        self.bufSize = 1024
        self.connected = False
        self.loggedIn = False
        self.dataMode = 'PORT'
        self.dataAddr = None
        self.dataPort = None

    def parse_reply(self):

        if self.controlSock is None:
            return
        try:
            reply = self.controlSock.recv(self.bufSize).decode('ascii')
        except Exception as e:
            print e
            return
        else:
            if 0 < len(reply):
                print('<< ' + reply.strip().replace('\n', '\n<< '))
                return int(reply[0]), reply
            else:
                # Server disconnected
                self.connected = False
                self.loggedIn = False
                self.controlSock.close()
                self.controlSock = None

    def connect(self, host, port):
        if self.controlSock is not None:
            # Close existing socket first
            self.connected = False
            self.loggedIn = False
            self.controlSock.close()
        self.controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.controlSock.connect((host, port))
        if self.parse_reply()[0] <= 3:
            self.connected = True
            self.controlSock.settimeout(1.0)

    def login(self, user, password):
        if not self.connected:
            return
        self.loggedIn = False
        self.controlSock.send(('USER %s\r\n' % user).encode('ascii'))
        if self.parse_reply()[0] <= 3:
            self.controlSock.send(('PASS %s\r\n' % password).encode('ascii'))
            if self.parse_reply()[0] <= 3:
                self.loggedIn = True

    def quit(self):
        if not self.connected:
            return
        self.controlSock.send(b'QUIT\r\n')
        self.parse_reply()
        self.connected = False
        self.loggedIn = False
        self.controlSock.close()
        self.controlSock = None

    def mkd(self, dir_name):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(b'MKD %s\r\n' % dir_name)
        self.parse_reply()

    def rmd(self, dir_name):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(b'RMD %s\r\n' % dir_name)
        self.parse_reply()

    def pwd(self):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(b'PWD\r\n')
        self.parse_reply()

    def cdup(self):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(b'CDUP\r\n')
        self.parse_reply()

    def cwd(self, path):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(('CWD %s\r\n' % path).encode('ascii'))
        self.parse_reply()

    def help(self):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(b'HELP\r\n')
        self.parse_reply()

    def type(self, t):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(('TYPE %s\r\n' % t).encode('ascii'))
        self.parse_reply()

    def pasv(self, pasv_type):
        self.controlSock.send(b'PASV %s\r\n' % pasv_type)
        reply = self.parse_reply()
        if reply[0] <= 3:
            m = re.search(r"\((\w*.+)", reply[1])
            self.dataAddr = m.group(0)[1: m.group(0).index(',')]
            self.dataPort = m.group(0)[m.group(0).index(',')+1: m.group(0).index(')')]
            self.dataMode = 'PASV'

    def nlst(self):
        if not self.connected or not self.loggedIn:
            return
        self.pasv('NLST')
        if self.dataMode != 'PASV':
            # Currently only PASV is supported
            return
        dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        dataSock.connect((self.dataAddr, int(self.dataPort)))
        self.controlSock.send(b'NLST\r\n')
        time.sleep(0.5)
        # Wait for connection to set up
        while True:
            try:
                data = dataSock.recv(self.bufSize)
                print "recv data:", data
                if len(data) == 0:
                    # Connection close
                    print 'no data'
                    break
                print(data.decode('ascii').strip())
            except Exception as e:
                # Connection closed
                print e
                break
        dataSock.close()
        self.parse_reply()

    def delete(self, file_name):
        if not self.connected or not self.loggedIn:
            return
        self.controlSock.send(('DELETE %s\r\n' % file_name).encode('ascii'))
        self.parse_reply()

    def retr(self, filename):
        if not self.connected or not self.loggedIn:
            return
        self.pasv('RETR')
        if self.dataMode != 'PASV':
            # Currently only PASV is supported
            return
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        data_socket.connect((self.dataAddr, int(self.dataPort)))
        self.controlSock.send(('RETR %s\r\n' % filename).encode('ascii'))
        file_out = open(filename, 'wb')
        time.sleep(0.5)
        # Wait for connection to set up
        data_socket.setblocking(False)
        # Set to non-blocking to detect connection close
        while True:
            try:
                data = data_socket.recv(self.bufSize)
                if len(data) == 0:
                    # Connection close
                    break
                file_out.write(data)
            except Exception as e:
                print e
                # Connection closed
                break
        file_out.close()
        data_socket.close()
        self.parse_reply()

    def stor(self, filename):
        if not self.connected or not self.loggedIn:
            return
        self.pasv('STOR')
        if self.dataMode != 'PASV':
            # Currently only PASV is supported
            return
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        data_socket .connect((self.dataAddr, int(self.dataPort)))
        self.controlSock.send(('STOR %s\r\n' % filename).encode('ascii'))
        data_socket .send(open(filename, 'rb').read())
        data_socket .close()
        self.parse_reply()

if __name__ == '__main__':
    server_address = '127.0.0.1'
    server_port = 12345
    hello_str = '''
Hello User, please input following index to select command:
1. login
11. quit
12. help
    '''
    login_str = '''
Hello User, please input following index to select command:
2. check current working directory
3. change working directory
4. back to parent directory
5. check file list under current directory
6. make new directory
7. delete directory
8. delete file
9. upload file
10. download file
11. quit
12. help
    '''

    client = FTPClient()
    client.connect(server_address, server_port)
    while True:
        if not client.loggedIn:
            index = raw_input(hello_str)
        else:
            index = raw_input(login_str)

        try:
            if index == '1':
                username = raw_input('Please input username')
                password = raw_input('Please input password')
                client.login(username, password)
            elif index == '2':
                client.pwd()
            elif index == '3':
                new_dir = raw_input('Please input the dir you want change')
                client.cwd(new_dir)
            elif index == '4':
                client.cdup()
            elif index == '5':
                client.nlst()
            elif index == '6':
                dir_name = raw_input('Please input new dir name')
                client.mkd(dir_name)
            elif index == '7':
                dir_name = raw_input('Please input new dir name')
                client.rmd(dir_name)
            elif index == '8':
                file_name = raw_input('Please input file name to delete')
                client.delete(file_name)
            elif index == '9':
                file_name = raw_input('Please input file name to upload')
                client.stor(file_name)
            elif index == '10':
                file_name = raw_input('Please input file name to download')
                client.retr(file_name)
            elif index == '11':
                client.quit()
                break
            elif index == '12':
                client.help()
            else:
                print "Please input correct index"

        except Exception as e:
            print "client encounter unknown problem"
            # print e
            continue



