__author__ = 'kittuov'
from django.utils import timezone


def environ(request):
    print(request.environ)
