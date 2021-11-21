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

import socket
from threading import Thread
from utils import *
import json
import os
import uuid
# import time

KEY = "aT6RJSmscMoxmgzViwlq5uXBBa04TJ4qr45dFYvlfTY="
WELCOMEMSG = "You are welcome to the amazing darkarmy channel"

class server_thread(Thread):
    def __init__(self, c, ip: int, port: int):
        Thread.__init__(self)
        self.c = c
        self.ip = ip
        self.port = port

    def run(self):

        self.hostandip = str(self.ip)+':'+str(self.port)
        users[self.hostandip] = 0

        while True:

            try:
                cdata = self.c.recv(1024)
            except:
                self.c.close()
                break

            encoded_message = cdata.decode("utf-8")
            f = Fernet(KEY)

            try:
                data = f.decrypt(bytes(encoded_message, 'utf-8'))
            except:
                self.send_error(self.c, 102)
                self.c.close()
                break

            if data:
                data = json.loads(data.decode("utf-8"))
                self.data = data

                if 'userid_connection' in data:
                    if 'password' in data:
                        Thread(target=self.userid_connection).start()

                elif 'user_register' in data:
                    if 'password' in data:
                        Thread(target=self.user_register).start()

                elif 'msg_type' in data:
                    if 'msg' in data:
                        Thread(target=self.sendmessage).start()


            else:
                self.c.close()
                break

        del users[self.hostandip]
        self.c.close()

    def user_register(self):
        user_id = uuid.uuid4().hex
        path = f"db/user/{user_id}/"

        if not os.path.exists(f"{path}"):
            os.makedirs(path)
#            os.makedirs(path + "/msg")
            if not os.path.exists(f"{path}/profil.json"):

                user_for_connection = {
                    'user_id' : user_id,
                    'user_name' : self.data['user_register'],
                    'password' : self.data['password'],
                }
                json_dumps(user_for_connection)

                with open(f"{path}/profil.json", 'w', encoding='utf-8') as f:
                    json.dump(user_for_connection, f, ensure_ascii=False, indent=2)

                self.send_data(self.c, user_for_connection)
                usersbyid[user_for_connection["user_id"]] = self.c
                self.user_id = self.data['user_register']
                users[self.hostandip] = 1
                self.send_info(self.c, WELCOMEMSG)

            else:
                self.send_error(self.c, 201)

        else:
            self.send_error(self.c, 201)

    def userid_connection(self):

        user_id = self.data['userid_connection']
        path = f"db/user/{user_id}/"

        if os.path.exists(f"{path}/profil.json"):

            with open(f"{path}/profil.json", 'r', encoding='utf-8') as f:
                fdata = json.load(f)

            if fdata['user_id'] == self.data['userid_connection']:
                if fdata['password'] == self.data['password']:

                    self.user_id = fdata["user_id"]
                    usersbyid[user_id] = self.c
                    users[self.hostandip] = 1
                    self.send_info(self.c, WELCOMEMSG)

    def sendmessage(self):
        if users[self.hostandip] == 1:
            message_to_sender = {
                'msg_type' : 'msg',
                'from_id' : self.user_id,
                'from_user_name' : self.get_info_from_user_id(self.user_id, 'user_name'),
                'msg' : self.data['msg'],

            }
            sender_id = self.data['sender_id']
            try:
                usersbyid[sender_id].send(encrypt(KEY, str(json_dumps(message_to_sender))))
            except:
                pass
        # else:

        #     user_id = self.data['userid_connection']
        #     path = f"db/user/{user_id}/msg/"

        #     if os.path.exists(f"{path}"):
        #         message_to_sender = {
        #             'from_id' : self.user_id,
        #             'send_msg' : self.data['msg'],
        #             'from_user_name' : self.get_info_from_user_id(self.data['sender_id'], 'user_name'),
        #             'time' : time.time,
        #         }

        #         user_id = uuid.uuid4().hex
        #         path = f"db/user/{user_id}/"

        #         with open(f"{path}/profil.json", 'r+', encoding='utf-8') as f:
        #             fdata = json.load(f)
        #             fdata.update(message_to_sender)
        #             f.seek(0)
        #             json.dump(fdata, f, ensure_ascii=False, indent=2)

    def get_info_from_user_id(self, user_id: str, value: str):
        try:
            with open(f"db/user/{user_id}/profil.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data[value]
        except:
            pass

    def send_error(self, c, n):
        error = {'error' : n}
        self.c.send(encrypt(KEY, str(json_dumps(error))))

    def send_info(self, c, info):
        info = {'info' : info}
        self.c.send(encrypt(KEY, str(json_dumps(info))))

    def send_data(self, c, msg):
        self.c.send(encrypt(KEY, str(json_dumps(msg))))

def start_server(host = '', port = 8080):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))

    global users, usersbyid
    users = {}
    usersbyid = {}

    print("socket binded to port", port,"...")

    while True:

        s.listen(5)
        (c, (ip,port)) = s.accept()
        thread = server_thread(c, ip, port)
        thread.start()

    s.close()

if __name__ == '__main__':
    start_server()
