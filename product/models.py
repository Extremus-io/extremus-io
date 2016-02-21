from django.db import models
from .validators import validate_id, validate_module_id


class Chipset(models.Model):
    name = models.CharField(max_length=30, help_text="name of chipset")
    oem = models.CharField(max_length=30, help_text="maker of the chip", verbose_name="OEM")

    def __str__(self):
        return "%s (%s)" % (self.name, self.oem)

# TODO: chipset is used to add some basic functionality automatically (modules)


"""
    This contains the definition for a the Product that is going to connect
        1. ID is like GAE app-id.
        2. name is the one that is to be displayed in case required
TODO:   3. chipset is used to add some basic functionality automatically
"""


class Product(models.Model):
    def __init__(self, *args, **kwargs):
        # get modules that belong to this product while initializing the object
        super().__init__(*args, **kwargs)
        if self.id is not None:
            self.modules = Module.objects.filter(product=self)

    id = models.CharField(unique=True, primary_key=True, verbose_name="Product ID", max_length=30,
                          help_text="Used to identify product. It has to be unique, It cannot be edited",
                          validators=[validate_id])
    description = models.TextField(max_length=600, default="No description provided")
    name = models.CharField(help_text="Displayed in controller and your app", max_length=30)
    chipset = models.ForeignKey(Chipset)
    code = models.FileField(verbose_name="Python Code", blank=True)

    def __str__(self):
        return self.id


class Module(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.methods =

    module_id = models.CharField(verbose_name="Module ID", max_length=30,
                                 help_text="has to be UNIQUE for a product",
                                 validators=[validate_id, validate_module_id])
    description = models.TextField(max_length=500, default="No description provided")
    is_core = models.BooleanField(default=False)
    raw_methods = models.TextField(verbose_name="Methods", help_text="Enter ONE prototype per line",
                                   max_length=1000, default="", blank=True)
    product = models.ForeignKey(Product)

    class Meta:
        unique_together = (("module_id", "product"),)

    def __str__(self):
        return "%s.%s"%(self.product.id, self.module_id)
