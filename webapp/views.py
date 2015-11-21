from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response


def index(request):
    get_token(request)
    return render_to_response('index.html')


def sw_import(request):
    return HttpResponse("importScripts('static/bower_components/platinum-sw/service-worker.js');", content_type="application/javascript")
