# -*- coding: utf-8 -*-
import asyncio
import random
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import blivedm
from blivedm.database import Message, base

DATABASE = 'postgresql'
USER = ''
PASSWORD = ''
HOST = 'localhost'
PORT = '5432'
DBNAME = 'bilibili'
CONNECT_STR = '{}://{}:{}@{}:{}/{}'.format(DATABASE, USER, PASSWORD, HOST, PORT, DBNAME)


engine = create_engine(CONNECT_STR)

SessionClass = sessionmaker(engine)
session = SessionClass()

base.metadata.create_all(bind=engine)


# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
   510,
]


async def main():
    await run_multi_client()


async def run_single_client():
    """
    演示监听一个直播间
    """
    room_id = random.choice(TEST_ROOM_IDS)
    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl=True)
    handler = MyHandler()
    client.add_handler(handler)

    client.start()
    try:
        # 演示5秒后停止
        await asyncio.sleep(5)
        client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


async def run_multi_client():
    """
    演示同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id) for room_id in TEST_ROOM_IDS]
    handler = MyHandler()
    for client in clients:
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    
    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')
        msg = Message(uid=message.uid, 
                rid=client.room_id,
                uname=message.uname,
                msg=message.msg,
                time=datetime.fromtimestamp(message.timestamp/1000),
                privilege_type=message.privilege_type)
        session.add(msg)
        session.commit()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
