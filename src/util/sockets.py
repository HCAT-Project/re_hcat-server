import socketio
from random import randint

sio_server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio_server.event
async def connect(sid, environ, auth):
    print(auth)
    print(f"{sid} connected")


@sio_server.event
async def disconnect(sid):
    print(f"{sid} disconnected")


@sio_server.event
async def private_message(sid, data):
    print(f"{sid} sent message {data}")
    await sio_server.emit(
        "message",
        {
            "type": "friend_msg",
            "friend_id": data["user_id"],
            "friend_name": "shipowka",
            "friend_nick": "shipowka",
            "rid": randint(1000000, 9999999),
            "time": 123123123,
            "user_id": data["user_id"],
            "msg": {"msg_chain": [{"msg": data["msg"], "type": "text"}]},
        },
    )
