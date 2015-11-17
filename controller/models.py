from django.db import models
import random
from django.contrib.auth.models import User
from djwebsockets.decorator import Namespace
from djwebsockets.server import WebSocketServer
from djwebsockets.websocket import BaseWSClass
from djwebsockets.mixins.wsgi import WSGIMixin
import json
from websockets import WebSocketClientProtocol
import asyncio


class ApiKeyManager(models.Manager):
    CHARS = "1234567890!@#$%^&*()"
    KEY_SIZE = 10

    def create_key(self):
        while True:
            key = self.generate_rand_key()
            try:
                self.get(key = key)
            except ApiKey.DoesNotExist:
                apikey = ApiKey.manager.create(key=key)
                apikey.save()
                return apikey

    def generate_rand_key(self):
        return "".join(random.choice(self.CHARS) for _ in range(self.KEY_SIZE))


class ApiKey(models.Model):
    key = models.CharField(max_length=10)
    date_created = models.DateTimeField(auto_now=True)
    removed_flag = models.BooleanField(default=False)
    manager = ApiKeyManager()


class ControllerUser(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    user = models.ForeignKey(User, rel=models.OneToOneRel)
    api_keys = models.ManyToManyField(ApiKey)

    def __str__(self):
        return self.user.username


class Controller(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.websocket = WebSocketServer.get_websocket_by_id(self.ws_id)
        self.online = self.websocket is not None

    def __str__(self):
        return self.name

    name = models.CharField(max_length=20, default="New controller")
    api_key = models.ForeignKey(ApiKey)
    modules = models.CharField(max_length=1000, blank=True)
    ws_id = models.PositiveIntegerField(blank=True)
    online = models.BooleanField(default=False)

    def go_online(self, ws_id):
        self.ws_id = ws_id
        self.save()
        self.online = True

    def go_offline(self):
        self.ws_id = -1
        self.save()
        self.online = False

    def get(self):
        raise NotImplemented

    def set(self):
        raise NotImplemented

    def pub(self):
        raise NotImplemented

    def sub(self):
        raise NotImplemented

    def unsub(self):
        raise NotImplemented


def get_controller(key):
    try:
        api_key = ApiKey.manager.get(key=key)
    except ApiKey.DoesNotExist:
        return None
    try:
        cont = Controller.objects.get(api_key=api_key)
    except Controller.DoesNotExist:
        cont = Controller(api_key=api_key)
        cont.save()
    return cont


@Namespace('controller/')
class ControllerWebSocket(BaseWSClass):
    API_KEY = "APIKEY"

    @classmethod
    def on_connect(cls, socket, path):
        data = {"get": "auth"}
        socket.send(json.dumps(data))
        socket.auth = lambda: None
        socket.auth = False
        print("Controller Connected")

    @classmethod
    def on_message(cls, socket, message):
        if not socket.auth:
            if cls.authenticate(message, socket):
                print("Controller Authenticated")
                return
            else:
                return
        print("received: {}".format(message))
        socket.send(" GOT {}".format(message))
        # try:
        #     msg = json.loads(message)
        #     to = msg.get("to")
        # except:
        #     pass
        #TODO: implement PROTOCOL

    @classmethod
    def on_close(cls, socket):
        key = cls.get_api_key(socket)
        if key is not None:
            cont = get_controller(key)
            if cont is not None:
                cont.go_offline()
        print("controller disconnected")

    @staticmethod
    def authenticate(message, socket):
        data = json.loads(message)
        key = data.get(ControllerWebSocket.API_KEY, None)
        if key is None:
            data = {"auth": False, "reason": "No API_KEY"}
            socket.send(json.dumps(data))
            socket.close()
            print("make sure to send apikey first to authenticate and identify the device")
            return False
        controller = get_controller(key)
        if controller is None:
            data = {"auth": False, "reason": "Invalid Key"}
            socket.send(json.dumps(data))
            socket.close()
            print("The key entered is not valid")
            return False
        controller.websocket = socket
        controller.online = True
        controller.go_online(socket.id)
        socket.auth = True
        data = {"auth": True}
        socket.send(json.dumps(data))
        socket.key = lambda: None
        socket.key = key
        return True

    @staticmethod
    def get_api_key(socket):
        try:
            return socket.key
        except AttributeError:
            return None


@Namespace('user/')
class UserWebSocket(WSGIMixin, BaseWSClass):
    @classmethod
    def on_connect(cls, socket, path):
        print("CONNECTED")
        print(socket.user)

    @classmethod
    def on_message(cls, socket, message):
        try:
            msg = json.loads(message)
            to = msg.get("to")
            cont = WebSocketServer.get_websocket_by_id(int(to))
            try:
                print("Sending data to {}".format(cont.key))
            except:
                pass
            if cont is not None:
                cont.send(msg.get('msg', "blank"))
        except:
            pass