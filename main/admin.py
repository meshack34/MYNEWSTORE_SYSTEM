# pylint: disable=W0401
from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register([
    SupplierType,
    Supplier,
    Purchase_Order,
    Item_group,
    Item_category,
    Item,
    Stock_Receipt,
    UOM,
    Company_details,
    Ingredient,
    Branch,
    
])
