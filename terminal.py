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

from client import ConnectServer
from passwordgenerator import pwgenerator
from utils import *
import json
import threading
import os
import time
import asyncio
import time

class terminal():
    def __init__(self):

        terminal_option = input("[1] Connect host, [2] Add host : ")
        if terminal_option == '1':
            self.connect_host()
        elif terminal_option == '2':
            self.append_host()

    def connect_host(self):

        print('Host avalaible : ')

        for dir in self.listdirs(r"data/servers/user/"):
            print(dir)

        host_name = input('Server name : ')
        user_name = input('User name : ')

        try:
            with open(f'data/servers/user/{host_name}/info.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            raise FileNotFoundError('FileNotFoundError')

        self.key = data['key']
        self.username = user_name

        s = ConnectServer(data['host'], int(data['port']), data['key'])
        self.s = s

        keypath = f"data/servers/user/{host_name}/"
        keyfile = f"data/servers/user/{host_name}/{user_name}.json"

        if not os.path.exists(f'{keypath}'):
            os.makedirs(keypath)

        if os.path.isfile(keyfile):
            with open(f'{keypath}/{user_name}.json', 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            self.myuserdata = user_data
            s.login(user_data['user_id'], user_data['password'])
            print('Your login is', user_data['user_id'])
            self.terminal_conversation()

        elif not os.path.isfile(keyfile):

            register_data = s.register(user_name, pwgenerator.generate())
            self.myuserdata = register_data

            with open(f'{keypath}/{user_name}.json', 'w', encoding='utf-8') as f:
                user_data = json.dump(json.loads(register_data), f)

            print('Your login is', register_data['user_id'])
            self.terminal_conversation()

    def recv_message(self):
        time.sleep(0.5)
        s = self.s
        while True:
            sender_id = input("Sender id : ")
            sender_msg = input("message : ")
            if not sender_id or not sender_msg:
                print('You have not typed any sender user d or message')
            else:
                self.s.sendmsg(sender_id, sender_msg)
                print('msg :', self.username, '(', self.myuserdata['user_id'], ')', ':', sender_msg)
                time.sleep(0.2)

    def terminal_conversation(self):

        s = self.s
        threading.Thread(target=self.recv_message).start()

        while True:
            data = s.recv(1024)
            decodedata = decrypt(self.key, data)
            decodedata = json.loads(decodedata.decode("utf-8"))

            if 'msg_type' in decodedata:
                if decodedata['msg_type'] == 'msg':
                    from_id = decodedata['from_id']
                    print('msg :', decodedata['from_user_name'], '(', decodedata['from_id'], ')', ':', decodedata['msg'])

            elif 'info' in decodedata:
                print("INFO :", decodedata['info'])

            elif 'error' in decodedata:
                if decodedata['error'] == 101:
                    print("ERROR :","Error for abusif data send")
                if decodedata['error'] == 102:
                    print("ERROR :","No valid KEY")
                if decodedata['error'] == 201:
                    print("ERROR :","The user already exists")

    def append_host(self):

        host_name = input('Server name : ')
        ip = input('Host ip : ')
        port = input('Host port : ')
        key = input('Key host : ')

        info_host = {
            "host": ip,
            "port": port,
            "key": key
        }

        os.makedirs(f'data/servers/user/{host_name}/')
        with open(f'data/servers/user/{host_name}/info.json', 'w', encoding='utf-8') as f:
            json.dump(info_host, f, ensure_ascii=False, indent=2)

        print('Host added with success !')

    def listdirs(self, path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

if __name__ == '__main__':
    terminal()
