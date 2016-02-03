from django.core.exceptions import ValidationError
from django.apps import AppConfig

EXCLUDED_CHARS = "!@#$%^&~`*()_=+/][{};':<>/? \\|,."


def validate_id(value):
    try:
        int(value[0])
        raise ValidationError("id cannot start with a number")
    except ValueError:
        pass
    value = str(value)
    for item in EXCLUDED_CHARS:
        if value.__contains__(item):
            raise ValidationError("id cannot have '%s'" % item)


def validate_module_id(value):
    pass


