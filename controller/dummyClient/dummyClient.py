import asyncio
import websockets
import sys
from threading import Thread,Event
import json

global inputtask
exitmsg = asyncio.Future()

@asyncio.coroutine
def hello(ApiKey):
    print("connecting to server")
    websocket = yield from websockets.connect('ws://localhost/ws/controller/', extra_headers={"APIKEY": ApiKey})
    print("connecting to inputDeamon")
    yield from websocket.send(json.dumps({"APIKEY": ApiKey}))
    while True:
        global inputtask
        inputtask = asyncio.Future()
        receivetask = asyncio.async(websocket.recv())
        connectiontask = asyncio.async(websocket.connection_closed)
        done, pending = yield from asyncio.wait([inputtask, receivetask, connectiontask, exitmsg], return_when=asyncio.FIRST_COMPLETED)
        if receivetask in done:
            if receivetask.result() == None:
                break
            print("<< "+receivetask.result())
        else:
            receivetask.cancel()
        if inputtask in done:
            a = inputtask.result()
            print(">> {}".format(a))
            yield from websocket.send(str(a))
        else:
            inputtask.cancel()

        if connectiontask in done:
            print("Socket closed")
            break
        if exitmsg in done:
            print("Exiting client...")
            break
    yield from websocket.close()


def exitLoop():
    exitmsg.set_result("DONE")


def listenInput():
    global inputtask
    while True:
        a = input()
        if a == "--exit--":
            loop.call_soon_threadsafe(exitLoop)
            break
        loop.call_soon_threadsafe(inputData, inputtask, a)


def inputData(future, data):
    future.set_result(data)


def run_socket(loop,ApiKey):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hello(ApiKey))


loop = asyncio.get_event_loop()
ApiKey = input("APIKEY:")
thread = Thread(target=run_socket, args=(loop, ApiKey))
thread.start()
listenInput()
