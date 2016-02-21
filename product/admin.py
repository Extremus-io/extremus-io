from django.contrib import admin
from .models import Product, Module, Chipset


class ModuleInline(admin.StackedInline):
    model = Module
    exclude = ['is_core']
    extra = 0
    fieldsets = (("Edit", {
        'fields': ('module_id', 'description', 'raw_methods'),
        'classes': ('collapse',)
    }),)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ModuleInline
    ]

admin.site.register(Chipset)
# Register your models here.
