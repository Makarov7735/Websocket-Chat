"""

*** Python websocket server ***

Date of creation - tus, 23 nov 2021 y. at 23:11
Made by Egor Makarov

"""
import asyncio
import websockets
import sqlite3
import json
import time
import sys


class Server:

    def __init__(self, host, port):
        self.users = dict()
        self.online_users = 0
        self.host = host
        self.port = port
        
    async def main_server(self):
        print('Server started...')
        async with websockets.serve(self.listen_sockets, self.host, self.port):
            await asyncio.Future() 

    async def send_data_to_sockets(self, data):
        data_json = json.dumps(data)
        for user in self.users:
            await user.send(data_json)

    async def add_user(self, websocket, username):
        self.users[websocket] = username
        self.online_users += 1
        await self.send_online()
        print('#User', username, 'join to chat')

    async def remove_user(self, websocket):
        del self.users[websocket]
        self.online_users -= 1
        await self.send_online()
    
    async def add_message_to_db(self, message, user):
        db = sqlite3.connect('db.sqlite3')
        cur = db.cursor()
        date = str(time.time())
        cur.execute(f'''INSERT INTO messages (user, message, date) VALUES ("{user}", "{message}", "{date}")''')  
        db.commit()
        db.close()
    
    async def send_previous_messages(self, websocket):
        db = sqlite3.connect('db.sqlite3')
        cur = db.cursor()
        for message in cur.execute(f'''SELECT * FROM messages ORDER BY date'''):
            if message != ('', '', '', 0):
                ttuple = time.localtime(float(message[2]))
                mtime = time.strftime('%b %d %H:%M', ttuple)
                data = {
                    'status': 'message',
                    'name': message[0],
                    'data': message[1],
                    'date': mtime
                }
                data_json = json.dumps(data)
                await websocket.send(data_json)
        db.close()

    async def send_online(self):
        data = {
            'status': 'online',
            'data': self.online_users
        }
        await self.send_data_to_sockets(data)

    async def send_message_to_sockets(self, websocket, data):
        print('#User', self.users[websocket], 'send message -> ', data['data'])
        ttuple = time.localtime(time.time())
        mtime = time.strftime('%b %d %H:%M', ttuple)
        data['name'] = self.users[websocket]
        data['date'] = mtime
        await self.send_data_to_sockets(data)

    async def listen_sockets(self, websocket):
        try:
            while True:
                data_json = await websocket.recv()
                data = json.loads(data_json)

                if data['status'] == 'username':
                    await self.send_previous_messages(websocket)
                    await self.add_user(websocket, data['data'])

                if data['status'] == 'message':
                    await self.send_message_to_sockets(websocket, data)
                    await self.add_message_to_db(data['data'], self.users[websocket])

        except (websockets.exceptions.ConnectionClosedOK,
                websockets.exceptions.ConnectionClosedError) as e:
            print('#User', self.users[websocket], 'left chat')
        finally:
            await self.remove_user(websocket)


def main():
    try:
        host, port = sys.argv[1], sys.argv[2]
    except IndexError:
        host, port = '127.0.0.1', '8000'
    server = Server(host, port)
    try:
        asyncio.run(server.main_server())
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()