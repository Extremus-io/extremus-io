from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, logout as auth_logout
import json as JSON


def login(request):
    if request.method == 'GET':
        form = AuthenticationForm()
        json = []
        for field in form.fields:
            json += [field_to_json(form, field)]
        return HttpResponse(JSON.dumps(json))
    request.POST = JSON.loads(request.body.decode('utf-8'))
    form = AuthenticationForm(request=request, data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        return HttpResponse(JSON.dumps({'auth': True}))
    else:
        return HttpResponse(JSON.dumps(form.errors))


def logout(request):
    auth_logout(request)
    return HttpResponse('{"logout": true}')


def field_to_json(form, field):
    output = {}
    output['id'] = field
    output['input_type'] = form.fields[field].widget.input_type
    output['label'] = form.fields[field].label.__str__()
    return output
