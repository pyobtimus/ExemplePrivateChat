# MIT License
#
# Copyright (c) 2021 pyobtimus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from utils import *
from threading import Thread
import socket
import json
import uuid

def sendata(s, key, data: str):
    s.send(encrypt(key, str(json_dumps(data))))

class ConnectServer():
    def __init__(self, host: str, port: int, key: str):
        self.host = host
        self.port = port
        self.key = key
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.s = s
        except:
            raise 'Server this is not exist'

    def register(self, user: str, pswd: str):
        user_for_register = {
            'user_register' : user,
            'password' : pswd
        }
        sendata(self.s, self.key, user_for_register)
        while True:

            data = self.s.recv(1024)
            decryptdata = decrypt(self.key, data)
            decryptstr = str(decryptdata)
            if 'user_id' and 'user_name' and 'password' in decryptstr:
                return decryptdata.decode("utf-8")

    def login(self, user_id: str, pswd: str):
        user_for_connection = {
            'userid_connection' : user_id,
            'password' : pswd
        }
        sendata(self.s, self.key, user_for_connection)
#        while True:

#            data = self.s.recv(1024)
#            decryptdata = decrypt(self.key, data)
#            if 'info' in str(decryptdata):
#                return decryptdata.decode("utf-8")

    def sendmsg(self, user_id: str, message: str):
        message_to_sender = {
            'msg_type' : 'msg',
            'sender_id' : user_id,
            'msg' : message,
        }
        sendata(self.s, self.key, message_to_sender)

    def recv(self, bytes):
        return self.s.recv(bytes)
