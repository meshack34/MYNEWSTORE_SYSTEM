from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SupplierTypeForm(forms.ModelForm):
    class Meta:
        model = SupplierType
        fields = "__all__"
        exclude = ('amount',)


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = "__all__"

class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = Item_category
        exclude = ('category_code',)

class  ItemGroupForm(forms.ModelForm):
    class Meta:
        model = Item_group
        exclude = ('group_code',)

class UOMForm(forms.ModelForm):
    class Meta:
        model = UOM
        fields = "__all__"
        
class stockbalanceCreateForm(forms.ModelForm):
    class Meta:
        model = stockbalanceCreate
        fields = ['item','branch','item_quantity',]  # Adjust fields as needed
        


        
class Purchase_OrdeSearchForm (forms.ModelForm):
    class Meta:
        model = Purchase_Order
        fields = ['po_number',]
        
class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch  
        exclude = ('branch_code',)

class Company_detailsForm(forms.ModelForm):
    class Meta:
        model = Company_details
        exclude = ('company_code',)
#Items 

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_category',  'item_group', 'item_UOM']
        

class StocksBalanceForm(forms.Form):
    model = stockbalanceCreate
    item = forms.ModelChoiceField(queryset=Item.objects.all(), empty_label=None)
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), empty_label=None)
    item_quantity = forms.IntegerField()
    
    
class UOMForm(forms.ModelForm):
    class Meta:
        model = UOM
        fields = "__all__"
        



class Purchase_OrderForm(forms.ModelForm):
    class Meta:
        model = Purchase_Order
        exclude = ['po_number', 'unit_price']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'branch_name': forms.Select(attrs={'class': 'form-select'}),
            'item': forms.Select(attrs={'class': 'form-select'}),
            'uomm': forms.Select(attrs={'class': 'form-select'}),
            'purchase_quantity': forms.TextInput(attrs={'class': 'form-control'}),
        }

class Stock_ReceiptForm(forms.ModelForm):
    class Meta:
        model = Stock_Receipt
        fields = "__all__"
    
    item_uom = forms.ModelChoiceField(queryset=UOM.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-select'}))
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super(Stock_ReceiptForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].widget = forms.Select(attrs={'class': 'form-select'})
        self.fields['item'].widget = forms.Select(attrs={'class': 'form-select'})
        self.fields['uomm'].widget = forms.Select(attrs={'class': 'form-select'})
        
        # Pre-fill the item_uom and quantity fields based on the selected Purchase Order
        selected_purchase_order = kwargs.pop('selected_purchase_order', None)
        if selected_purchase_order:
            self.fields['item_uom'].initial = selected_purchase_order.uomm
            self.fields['quantity'].initial = selected_purchase_order.purchase_quantity


        
class BOMForm(forms.ModelForm):
    class Meta:
        model = BOM
        fields = "__all__"


class BranchTransferForm(forms.ModelForm):
    class Meta:
        model = BranchTransfer
        exclude = ('transfer_date',)



class StockRequestForm(forms.ModelForm):
    class Meta:
        model = StockRequest
        fields = "__all__"


        
class BilledStockForm(forms.ModelForm):
    class Meta:
        model = BilledStock
        fields = "__all__"

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=101)
    last_name = forms.CharField(max_length=101)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']