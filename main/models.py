
from django.db import models
from django.utils import timezone
from .utils import generate_bom_id
from django.db.models import Sum
import uuid
# company and branch model


class Company_details(models.Model):
    class Choose_payment(models.TextChoices):
        PHONE = "Phone Number", "Phone Number"
        PAYBILL = "Paybill", "Paybill"
        TILL = "Till", "Till"
        CASH = "Cash", "Cash"
    company_name = models.CharField(max_length=250, ) #unique=True
    company_code = models.CharField(max_length=20, unique=True)
    company_location = models.CharField(max_length=255)
    preffered_mode_of_payment = models.CharField(max_length=255, choices=Choose_payment.choices, null=True)
    till_number = models.IntegerField()
    paybill_number = models.IntegerField()
    
    def __str__(self):
        return self.company_name
       
class Branch(models.Model):
    class Choose_Main_branch(models.TextChoices):
        Yes = "Yes", "Yes"
        No = "No", "No"
    branch_name = models.CharField(max_length=250, unique=True, null=True)
    branch_code =  models.CharField(max_length=20, unique=True)
    branch_location = models.CharField(max_length=200)
    main_branch = models.CharField(max_length=12, choices=Choose_Main_branch.choices, null=True)
    def __str__(self):
        return self.branch_name


# Create your models here.
class SupplierType(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    class ModeOfPayments(models.TextChoices):
        PHONE = "Phone Number", "Phone Number"
        PAYBILL = "Paybill", "Paybill"
        TILL = "Till", "Till"
        CASH = "Cash", "Cash"
        
    supplier_name = models.CharField(max_length=250)
    supplier_type = models.ForeignKey(SupplierType, on_delete=models.CASCADE, related_name='supplier_supplier_type')
    preferred_mode_of_payment = models.CharField(max_length=12, choices=ModeOfPayments.choices, null=True)
    physical_location = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=13)
    credit_days = models.IntegerField()
    def __str__(self):
        return self.supplier_name
    

class Item_category(models.Model):
    category_name = models.CharField(max_length=250,unique=True,)
    category_code = models.CharField(max_length=250, unique=True,)

    def __str__(self):
        return self.category_name

class Item_group(models.Model):
    group_name = models.CharField(max_length=250,unique=True,)
    group_code = models.CharField(max_length=250,unique=True,)
    

    def __str__(self):
        return self.group_name
    
class UOM(models.Model):   
    UOM_name = models.CharField(max_length=250)

    def __str__(self):
        return self.UOM_name
    


        
class Item(models.Model):
    item_name = models.CharField(max_length=250)
    item_code = models.CharField(max_length=255, unique=True,)
    item_category = models.ForeignKey(Item_category,on_delete=models.CASCADE, related_name='item_category')
    item_group = models.ForeignKey(Item_group,on_delete=models.CASCADE, related_name='item_group')
    item_UOM = models.ForeignKey(UOM, on_delete=models.CASCADE, related_name='item_uom')
    receveive_quantity =models.CharField(max_length=50, blank=True, null=True)
    receive_by =models.CharField(max_length=50, blank=True, null=True)
    issue_quantity =models.CharField(max_length=50, blank=True, null=True)
    issue_by =models.CharField(max_length=50, blank=True, null=True)
    issue_to =models.CharField(max_length=50, blank=True, null=True)
    created_by =models.CharField(max_length=50, blank=True, null=True)
    reorder_level =models.IntegerField(default='0',  blank=True, null=True)
    last_updated =models.DateTimeField(auto_now_add=False, auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True, auto_now=False)
   
   

    def __str__(self):
        return self.item_name
    @staticmethod
    def generate_itemcode():
        last_item = Item.objects.order_by('-item_code').first()
        if last_item:
            last_code = last_item.item_code.split('-')[-1]
            last_three_digits_itemcode = int(last_code)
        else:
            last_three_digits_itemcode = 0

        last_three_digits_itemcode += 1
        category_code = 'ITCODE-00-' + str(last_three_digits_itemcode).zfill(3)
        return category_code

class stockbalanceCreate(models.Model):
    item_quantity = models.IntegerField(null=True, blank=True, default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE,)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Add this field for the date of creation
    update_date = models.DateTimeField(auto_now=True, null=True, blank=True)  # Add this field for the date of creation
    class Meta:
        unique_together = ('branch', 'item')
        
    def __str__(self):
        return self.item.item_name

class Ingredient(models.Model):
    main_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ingredients_items_two', null=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ingredients_items', null=True)
    item_UOM = models.ForeignKey(UOM, on_delete=models.CASCADE, related_name='item_uom_ingredients')
    quantity = models.IntegerField(null=True)
    unit_price = models.DecimalField(max_digits=210, decimal_places=2, null=True)
    total_price = models.DecimalField(max_digits=210, decimal_places=2, null=True)
    
    def __str__(self):
        return str(self.item)
    
    

class Purchase_Order(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
    branch_name = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='purchase_branch')
    po_number = models.CharField(max_length=255, unique=True)
    # item = models.ForeignKey(Item, related_name='po_item_name', on_delete=models.CASCADE, null=True)
    # uomm = models.ForeignKey(UOM, related_name='po_UOMM', on_delete=models.CASCADE, null=True)
    ingredients = models.ManyToManyField(Ingredient, related_name='PO_ing', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    purchase_quantity = models.CharField(max_length=13)
    purchase_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
   

    def save(self, *args, **kwargs):
        # Calculate the unit_price based on the selected item
        if self.item:
            ingredient = Ingredient.objects.filter(main_item=self.item).first()
            if ingredient:
                self.unit_price = ingredient.unit_price
        super().save(*args, **kwargs)

    @property
    def unit_price(self):
        if self.ingredients.exists():
            return self.ingredients.first().unit_price
        return None

    def __str__(self):
        return self.po_number

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = generate_po_code()
        super().save(*args, **kwargs)



def generate_po_code():
    last_ponumber = Purchase_Order.objects.order_by('-id').first()
    if last_ponumber:
        last_ponumber_id = int(last_ponumber.po_number.split('-')[2].strip())
        new_ponumber_id = last_ponumber_id + 1
    else:
        new_ponumber_id = 1
    po_number = f"PO-NUM-{str(new_ponumber_id).zfill(3)}"
    return po_number




class Stock_Receipt(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirm', 'Confirm'),
    )
    orderstatus = models.CharField(max_length=500, null=True, choices=ORDER_STATUS_CHOICES, default='pending')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True,)
    branch_name = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='purchase_orders')
    stockreip = models.CharField(max_length=255, unique=True,)
    phone_number = models.CharField(max_length=500, null=True)
    receive_by = models.CharField(max_length=50, blank=True, null=True)
    item = models.ForeignKey(Item, related_name='po_item', on_delete=models.CASCADE, null=True)
    uomm = models.ForeignKey(UOM, related_name='po_uom', on_delete=models.CASCADE, null=True)
    ingredients = models.ManyToManyField(Ingredient, related_name='PO_ingredients', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    purchase_quantity = models.CharField(max_length=13)
    purchase_date = models.DateTimeField(auto_now_add=True, auto_now=False)
    update_date = models.DateTimeField(auto_now_add=False, auto_now=True)
    purchase_order = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE,null = True, blank=True )
    
    def save(self, *args, **kwargs):
        if not self.orderstatus:
            self.orderstatus = 'pending'
        
        if not self.stockreip:
            self.stockreip = generate_stockreceipt_code()
        
        super(Stock_Receipt, self).save(*args, **kwargs)

        
def generate_stockreceipt_code():
    last_stockreceipt = Stock_Receipt.objects.order_by('-id').first()
    if last_stockreceipt:
        last_stockreceipt_id = int(last_stockreceipt.stockreip.split('-')[2].strip())
        new_stockreceipt_id = last_stockreceipt_id + 1
    else:
        new_stockreceipt_id = 1
    stockreip = f"STOCKRECE-00-{str(new_stockreceipt_id).zfill(3)}"
    return stockreip


        
    
class StockRequest(models.Model):
    class TypeOfOrder(models.TextChoices):
        SALE = "Sale Order", "Sale Order"
        WORK = "Work Order", "Work Order"       
    order_type = models.CharField(max_length=12, choices=TypeOfOrder.choices, null=True)
    items = models.ManyToManyField(Item ,related_name='stock_request_items')
    item_UOM = models.ForeignKey(UOM, on_delete=models.CASCADE, related_name='item_uom_stock_request')
    consumed_quantity = models.IntegerField()
    
class StockEntry(models.Model):
    items = models.ManyToManyField(Item ,related_name='stock_entry_items')
    item_UOM = models.ForeignKey(UOM, on_delete=models.CASCADE, related_name='item_uom_stock_entry')
    quantity = models.IntegerField()
    
class BilledStock(models.Model):
    items = models.ManyToManyField(Item ,related_name='billed_stocks_items')
    item_UOM = models.ForeignKey(UOM, on_delete=models.CASCADE, related_name='item_uom_billed_stock')
    quantity = models.IntegerField()
    
class BranchTransfer(models.Model):
    from_branch = models.ForeignKey(Branch,on_delete=models.CASCADE, related_name='from_branch')
    to_branch = models.ForeignKey(Branch,on_delete=models.CASCADE, related_name='to_branch')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item',null=True)
    quantity = models.IntegerField(null=True)
    transfer_date = models.DateField(auto_now_add=True)

 
    
class BOM(models.Model):
    item = models.ForeignKey(Item, related_name='bom_item',on_delete=models.CASCADE,null=True)
    uomm = models.ForeignKey(UOM, related_name='bom_uom',on_delete=models.CASCADE,null=True)
    bom_id = models.CharField(max_length=255,unique= True)
    ingredients = models.ManyToManyField(Ingredient, related_name='bom_ingredients', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.bom_id = generate_bom_id()
        super(BOM, self).save(*args, **kwargs)
   

    
class Managepayment(models.Model):
    supplier_name = models.ForeignKey(Supplier,on_delete=models.CASCADE, related_name='suppeliername')
    
    def __str__(self):
        return self.supplier_name
    


class Purchase_Order_Item(models.Model):
    purchase_order = models.ForeignKey(Purchase_Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    purchase_quantity = models.PositiveIntegerField()









    
