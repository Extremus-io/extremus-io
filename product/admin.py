from django.contrib import admin
from .models import Product, Module, Chipset


class ModuleInline(admin.StackedInline):
    model = Module
    exclude = ['is_core']
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ModuleInline
    ]

admin.site.register(Product, ProductAdmin)
admin.site.register(Chipset)
# Register your models here.
