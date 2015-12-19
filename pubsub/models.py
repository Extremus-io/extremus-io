from django.db import models
import importlib


class Room(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients, self.ids = self._get_clients()

    name = models.CharField(max_length=30, unique=True)
    str_ids = models.CommaSeparatedIntegerField(max_length=500)

    def _get_clients(self):
        ids = self.sockets.split(",")
        clients = []
        for id in ids:
            si = SubIdentifier.objects.get(id=id)
            cls = si.get_cls()
            try:
                client = cls.objects.get(pk=si.identifier)
                clients.append(client)
            except:
                continue

        return clients, ids

    def add_client(self, client):
        subs = SubIdentifier.objects.filter(identifier=client.pk, cls_name=client.__class__.__name__, module=client.__module__)
        if len(subs) == 0:
            si = SubIdentifier(identifier=client.pk, cls_name=client.__class__.__name__, module=client.__module__)
            si.save()
        else:
            si = subs[0]
        if self.ids.count(str(si.pk)) == 0:
            self.clients.append(client)

    def remove_client(self, client):
        subs = SubIdentifier.objects.filter(identifier=client.pk, cls_name=client.__class__.__name__, module=client.__module__)
        if len(subs) == 0:
            si = SubIdentifier(identifier=client.pk, cls_name=client.__class__.__name__, module=client.__module__)
            si.save()
        else:
            si = subs[0]
        if self.ids.count(str(si.pk)) != 0:
            self.ids.remove(str(si.pk))
            for client in self.clients:
                if client.pk == si.pk:
                    self.clients.remove(client)

    def publish(self, source):
        data = ""
        for client in self.clients:
            client.send()


    @staticmethod
    def get_room_string(client):
        return client.__class__.__name__+"-"+str(client.pk)


class SubIdentifier(models.Model):
    module = models.CharField(max_length=40, verbose_name="Module location")
    cls_name = models.CharField(max_length=40, verbose_name="Class name")
    identifier = models.CharField(max_length=50, verbose_name="Identity in that class")

    def get_client(self):
        module = importlib.import_module(name=self.module)
        item = getattr(module, self.cls_name)
        item.get_instance("")
        return item



