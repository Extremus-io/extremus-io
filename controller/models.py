from django.db import models
import random
from django.contrib.auth.models import User
from djwebsockets.decorator import Namespace
from djwebsockets.server import WebSocketServer
from djwebsockets.websocket import BaseWSClass
from rest_framework.serializers import HyperlinkedModelSerializer
from djwebsockets.mixins.wsgi import WSGIMixin
import json


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
        self.online = True
        self.save()

    def go_offline(self):
        self.ws_id = -1
        self.online = False
        self.save()

    def save(self,*args,**kwargs):
        super().save(*args, **kwargs)
        update = ControllerSerializer(self)
        data = update.data
        data['type'] = 'update'
        self.pub(json.dumps(data))

    def get(self):
        raise NotImplemented

    def set(self):
        raise NotImplemented

    def pub(self, data):
        ControllerPubSub.pub(self, data)

    def sub(self):
        raise NotImplemented

    def unsub(self):
        raise NotImplemented


class ControllerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Controller
        fields = ('id', 'name', 'modules', 'online')


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
        data = {"type": "msg", "msg": message}
        cont = get_controller(socket.key)
        cont.pub(json.dumps(data))

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
        if not socket.user.is_authenticated():
            data = {'auth': False}
            socket.send(json.dumps(data))
        print(socket.id)

    @classmethod
    def on_message(cls, socket, message):
        #TODO: catch exception if msg is not parsable and send appropriate error message
        msg = json.loads(message)
        type = msg.get("type")
        if type == "send":
            to = msg.get("to")
            cont = WebSocketServer.get_websocket_by_id(int(to))
            if cont is not None:
                cont.send(msg.get('msg', "blank"))
        if type == "sub":
            to = msg.get("to")
            if to is not None:
                ControllerPubSub.sub(socket.id, to)
        if type == "unsub":
            to = msg.get("to")
            if to is not None:
                ControllerPubSub.unsub(socket.id, to)


class ControllerPubSub:
    room = {}

    @staticmethod
    def sub(userws, controller_id):
        try:
            cont = Controller.objects.get(id=int(controller_id))
        except Controller.DoesNotExist:
            data = {'error': {'code': 404, 'msg': 'controller with id {} doesnot exist'.format(controller_id)}}
            print(json.dumps(data))
            ws = WebSocketServer.get_websocket_by_id(userws)
            if ws is not None:
                ws.send(json.dumps(data))
            return
        room = ControllerPubSub.room.get(int(controller_id))
        if room is None:
            room = []
        room.append(userws)
        ControllerPubSub.room[int(controller_id)] = room
        print(ControllerPubSub.room)
        data = ControllerSerializer(cont).data
        data['sub'] = True
        data['type'] = 'update'
        ws = WebSocketServer.get_websocket_by_id(userws)
        if ws is not None:
            ws.send(json.dumps(data))
        print(json.dumps(data))

    @classmethod
    def unsub(cls, userws, controller_id):
        room = cls.room.get(int(controller_id))
        if room is not None:
            try:
                room.remove(userws)
                print('removed a user')
            except ValueError:
                pass

    @classmethod
    def pub(cls, cont, str_data):
        room = cls.room.get(cont.id, [])
        for ws_id in room:
            ws = WebSocketServer.get_websocket_by_id(ws_id)
            if ws is None:
                room.remove(ws_id)
            else:
                ws.send(str_data)

