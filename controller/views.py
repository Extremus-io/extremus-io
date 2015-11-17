from django.contrib.auth.models import AnonymousUser
from .models import Controller, ControllerUser, get_controller
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from json import dumps

# Create your views here.


class ControllerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Controller
        fields = ('id', 'name', 'modules', 'online')


@api_view(['GET'])
def ControllerList(request):
    try:
        keys = ControllerUser.objects.get(user=request.user).api_keys.all()
    except ControllerUser.DoesNotExist:
        ControllerUser.create(user=request.user)
        keys = ControllerUser.objects.get(user=request.user).api_keys.all()
    json = []
    for key in keys:
        cont = get_controller(key.key)
        if cont is not None:
            data = ControllerSerializer(cont, context={'request': request})
            json.append(data.data)
    return Response(json)


@api_view(['GET', 'PUT', 'DELETE'])
def ControllerView(request, pk):
    """
    Retrieve, update or delete a snippet instance.
    """
    try:
        controller = Controller.objects.get(pk=pk)
    except Controller.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    print(request.user)
    if not request.user.is_authenticated():
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        ControllerUser.objects.get(user=request.user)
    except ControllerUser.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = ControllerSerializer(controller, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ControllerSerializer(controller, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        controller.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
