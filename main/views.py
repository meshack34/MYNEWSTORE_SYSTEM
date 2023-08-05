from urllib import response
from django.contrib import messages
from .utils import *
import json, random, string, re
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from decimal import Decimal
import uuid


from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django_daraja.mpesa.core import MpesaClient
from django.shortcuts import redirect, render
from .models import *
from .forms import *
from django_daraja.mpesa import utils 
from django.views.generic import View
from decouple import config
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm
from django.contrib import messages
from .connecting_transaction_module import all_transaction_process, transaction_login
from .get_service_fields import get_service_fields, get_service_metadata
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Q

BASE_URL = "http://bharathbrandsdotin.pythonanywhere.com/api-alada/"


# home view
def home(request):
    request.session["mode"] = "client"
    return render(request, "home.html")



# register user
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(
                request, f"Your account has been created. You can log in now!"
            )
            return redirect("login")
    else:
        form = UserRegistrationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


# Add supplier type.
def add_supplier_type(request):
    form = SupplierTypeForm()
    context = {"form": form}
    return render(request, "add_supplier_type.html", context)


# To show supplier type
def show_supplier_type(request):
    suppliers = Supplier.objects.all()
    return render(request, "view_supplier_type.html", {"suppliers": suppliers})


# To edit supplier type
def edit_supplier_type(request):
    return render(request, "edit_supplier.html")


# add_supplier
def add_supplier(request):
    form = SupplierForm()

    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("views_suppliers")
        else:
            messages.info(request, message="Could not save supplier")
            return redirect("add_supplier")

    return render(request, "add_supplier.html", {"form": form})


# view_supplier
def views_suppliers(request):
    suppliers = Supplier.objects.all()
    print(suppliers)
    context = {"suppliers": suppliers}
    return render(request, "view_suppliers.html", context)


def add_product(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        item_code = Item.generate_itemcode()
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.item_code = item_code
            new_item.save()
            return redirect('show_product')
    else:
        form = ItemForm()
    return render(request, 'add_product.html', {'form': form})

# To show product

def show_product(request):
    search_query = request.GET.get('search_query')
    items = Item.objects.all()

    if search_query:
        items = items.filter(
            Q(item_name__icontains=search_query) |
            Q(item_code__icontains=search_query) |
            Q(item_category__category_name__icontains=search_query)
        )

    context = {"items": items}
    return render(request, "show_product.html", context)
# Add stocks balance

def add_stocks_balance(request):
    if request.method == 'POST':
        form = StocksBalanceForm(request.POST)
        if form.is_valid():
            item = form.cleaned_data['item']
            branch = form.cleaned_data['branch']
            item_quantity = form.cleaned_data['item_quantity']
            branch_item, created = stockbalanceCreate.objects.get_or_create(item=item, branch=branch)
            branch_item.item_quantity += item_quantity
            branch_item.save()
            return redirect('/stocks_balance')
    else:
        form = StocksBalanceForm()
    return render(request, 'add_stocks_balance.html', {'form': form})

def sort_by_date(items, date_attr, reverse=False):
    return sorted(items, key=lambda x: getattr(x, date_attr), reverse=reverse)

# show stock_balance
def stocks_balance(request):
    branches = Branch.objects.all()
    items = Item.objects.all()
    stock_balance_data = []
    search_query = request.GET.get('search_query')
    sort_by = request.GET.get('sort_by', 'created_date')  # Default to sorting by created_date if not provided
    sort_order = request.GET.get('sort_order', 'asc')  # Default to ascending order if not provided
     
    if search_query:
        items = items.filter(
            Q(item_name__icontains=search_query) |
            Q(item_code__icontains=search_query) |
            Q(item_category__category_name__icontains=search_query)
        )
     # Sorting logic based on the column clicked
    if sort_by == 'item_name':
        items = items.order_by('item_name' if sort_order == 'asc' else '-item_name')
    elif sort_by == 'item_code':
        items = items.order_by('item_code' if sort_order == 'asc' else '-item_code')

    for item in items:
         row_data = (item.item_name, item.item_code, item.item_category, item.item_group, [], item.stockbalancecreate_set.first().created_date if item.stockbalancecreate_set.exists() else None, item.stockbalancecreate_set.first().update_date if item.stockbalancecreate_set.exists() else None)
         for branch in branches:
            stock_balance_item = branch.stockbalancecreate_set.filter(item=item).first()
            quantity = stock_balance_item.item_quantity if stock_balance_item else 0
            row_data[4].append(quantity)
         stock_balance_data.append(row_data)
        

    return render(request, 'stocks_balance.html', {'stock_balance_data': stock_balance_data, 'stock_balance_data': stock_balance_data, 'branches': branches})




def edit_stocks_balance(request,item_id):
    item = get_object_or_404(Item, item_code=item_id)
    stock_balance_item =  stockbalanceCreate.objects.filter(item=item).last() 
    print('Error')
    
    if request.method == 'POST':
        form = stockbalanceCreateForm(request.POST, instance=stock_balance_item)
        if form.is_valid():
            form.save()
            return redirect('stocks_balance')  
    else:
        form = stockbalanceCreateForm(instance=stock_balance_item)
    
    context = {
        'form': form,
        'branch': branch,
        'item': item,
    }
    return render(request, 'edit_stocks_balance.html', context)



# To edit product
def edit_product(request, id):
    item = get_object_or_404(Item, id=item.id)
    items = requests.get(
        "http://bharathbrandsdotin.pythonanywhere.com/api-alada/item"
    ).json()
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("view_product", id=item.id)
    else:
        form = ItemForm(instance=item)
    return render(request, "edit_product.html", {"form": form, "items": items})


#purchase order



def StockEntry_withPO(request):
    if request.method == "POST":
        try:
            search_po = request.POST.get("search_po")
            if search_po == "search_po":
                search_po_id = request.POST.get("po_no")
                purchase_order = Purchase_Order.objects.filter(po_number=search_po_id)
                context = {'purchase_order': purchase_order}
                return render(request, 'StockEntry_withPO.html', context)

        except Exception as error:
            return render(request, 'error.html', {'error': error})
    else:
        return render(request, 'StockEntry_withPO.html')




def edit_purchase_order(request, purchase_order_id):
    purchase_order = get_object_or_404(Purchase_Order, id=purchase_order_id)
    items = Item.objects.all()
    uoms = UOM.objects.all()
    suppliers = Supplier.objects.all()
    branches = Branch.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("mainItem")
        supplier = Supplier.objects.get(id=supplier_id)
        branch_id = request.POST.get("branch")
        branch = Branch.objects.get(id=branch_id)
        ingredients_list = list(request.POST.getlist("ingredient"))
        uom_list = list(request.POST.getlist("mainUOM"))
        quantity_list = list(request.POST.getlist("quantity"))
        unit_price_list = list(request.POST.getlist("unit_price"))
        quantity_added_list = list(request.POST.getlist("quantity_added")) 
        
        purchase_order.supplier = supplier
        purchase_order.branch_name = branch
        purchase_order.ingredients.clear()  
        
        for i in range(len(ingredients_list)):
            ingredient = Item.objects.get(id=int(ingredients_list[i]))
            uom = UOM.objects.get(id=int(uom_list[i]))
            quantity = int(quantity_list[i])
            unit_price = float(unit_price_list[i])
            quantity_added = int(quantity_added_list[i]) 
            
            new_ingredient = Ingredient.objects.create(
                main_item=ingredient, item=ingredient, item_UOM=uom, quantity=quantity, unit_price=unit_price
            )
            purchase_order.ingredients.add(new_ingredient)  # Associate the ingredient with the purchase order
            
            # Update stock balance for the branch and ingredient
            branch_item, created = stockbalanceCreate.objects.get_or_create(item=ingredient, branch=branch)
            branch_item.item_quantity += quantity_added
            branch_item.save()
        
        purchase_order.save()
        purchase_orders = Purchase_Order.objects.all()  # Update purchase_orders
        context = {
            "purchase_order": purchase_order,
            "items": items,
            "uoms": uoms,
            "suppliers": suppliers,
            "branches": branches,
            "purchase_orders": purchase_orders,  # Include updated purchase orders
        }

        return redirect("/show_stock_receipts")
    else:
        form = Purchase_OrderForm()
   
    
            
    context = {
        # "stock_receipt":stock_receipt,
        "purchase_order": purchase_order,
        "items": items,
        "uoms": uoms,
        "suppliers": suppliers,
        
       
        "branches": branches,
        "purchase_orders": Purchase_Order.objects.all(),
        "form":form
    }
    return render(request, "edit_purchase_order.html", context)





def display_purchase_orders(request):
    purchase_orders = Purchase_Order.objects.all()
    stock_receipts = Stock_Receipt.objects.select_related("purchase_order")
    for data in stock_receipts:
        print(data.id)
        print(data.stockreip)
        print(data.branch_name)

    context = {
        "purchase_orders": stock_receipts,
        "stock_receipts": stock_receipts,
    }

    return render(request, "display_purchase_orders.html", context)




 


def StockEntry_withPO_edit(request, stock_receipt_id):
    stock_receipt = get_object_or_404(Stock_Receipt, id=stock_receipt_id)
    
    if request.method == 'POST':
        form = Stock_ReceiptForm(request.POST, instance=stock_receipt)
        if form.is_valid():
            form.save()
            return redirect('view_stock_receipt', stock_receipt_id=stock_receipt_id)
    else:
        form = Stock_ReceiptForm(instance=stock_receipt)
    
    context = {
        'stock_receipt': stock_receipt,
        'form': form,
    }
    return render(request, 'StockEntry_withPO_edit.html', context)



# views.py

from django.http import JsonResponse

def get_purchase_order_data(request):
    if request.method == "GET" and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        po_id = request.GET.get("po_id")
        try:
            purchase_order = Purchase_Order.objects.get(id=po_id)
            data = {
                "supplier_id": purchase_order.supplier_id,
                "branch_name_id": purchase_order.branch_name_id,
                "receive_by": purchase_order.receive_by,
                "items": [
                    {
                        "id": ingredient.item.id,
                        "uom_id": ingredient.item_UOM.id,
                        "quantity": ingredient.quantity,
                        "unit_price": ingredient.unit_price,
                    }
                    for ingredient in purchase_order.ingredients.all()
                ]
            }
            return JsonResponse(data)
        except Purchase_Order.DoesNotExist:
            pass

    return JsonResponse({"items": []})










def get_items(request):
    branch_id = request.GET.get('branch_id')
    items = stockbalanceCreate.objects.filter(branch_id=branch_id)
    item_list = []

    for item in items:
        item_data = {
            'id': item.id,
            'item_name': item.item.item_name
        }
        item_list.append(item_data)

    return JsonResponse({'items': item_list})


def StockEntry_withoutPO(request):
    form = Stock_ReceiptForm()
    uoms = UOM.objects.all()
    suppliers = Supplier.objects.all()
    branches = Branch.objects.all()

    if request.method == "POST":
        branch_id = request.POST.get("branch")
        receive_by = request.POST.get("receive_by")
        ingredients_list = list(request.POST.getlist("ingredient"))
        uom_list = list(request.POST.getlist("mainUOM"))
        quantity_list = list(request.POST.getlist("quantity"))
        unitprices_list = request.POST.getlist('unit_price')
        
        try:
            branch = get_object_or_404(Branch, id=branch_id)
            supplier_id = int(request.POST.get("supplier"))
            supplier = get_object_or_404(Supplier, id=supplier_id)
        except (ValueError, Branch.DoesNotExist):
            return render(request, 'error_template.html', {"message": "Invalid Branch ID"})
        except Supplier.DoesNotExist:
            return render(request, 'error_template.html', {"message": "Invalid Supplier ID"})

        new_Purchase_Order = Stock_Receipt.objects.create(
            supplier=supplier, receive_by=receive_by, branch_name=branch
        )

        for i in range(len(ingredients_list)):
            ingredient_id = int(ingredients_list[i])
            uom = get_object_or_404(UOM, id=int(uom_list[i]))
            quantity = int(quantity_list[i])
            unit_price = Decimal(unitprices_list[i])
            ingredient = get_object_or_404(stockbalanceCreate, id=ingredient_id, branch=branch)
            print("quantity before:", ingredient.item_quantity)
            item_quantity = ingredient.item_quantity + quantity
            print("quantity after:", item_quantity)
            ingredient.item_quantity = item_quantity
            ingredient.save()

            ingredient.receveive_quantity = quantity

            total_price = Decimal(unit_price) * quantity
            newStockReceip_withoutPO = Ingredient.objects.create(
                main_item=new_Purchase_Order.item, item=ingredient.item, item_UOM=uom, quantity=quantity,
                total_price=total_price, unit_price=unit_price
)
        

            newStockReceip_withoutPO.item.save()

            new_Purchase_Order.ingredients.add(newStockReceip_withoutPO)

        return redirect("show_stock_receipts")

    context = {
        "form": form,
        "uoms": uoms,
        "suppliers": suppliers,
        "branches": branches,
        "purchase_orders": Stock_Receipt.objects.all(),  # Include this to pass the purchase orders to the template
    }

    return render(request, 'StockEntry_withoutPO.html', context)

def show_stock_receipts2(request, stock_receipt_id):
    stock_receipt = get_object_or_404(Stock_Receipt, id=stock_receipt_id)
    branches = Branch.objects.all()
    ingredients = Ingredient.objects.all()
    stock_receipts = Stock_Receipt.objects.all()
    if request.method == "POST":
        price = request.POST.get("price")
        received_by = request.POST.get("received_by")

        stock_receipt.price = price
        stock_receipt.received_by = received_by
        stock_receipt.save()

        return redirect('stock_receipt_detail', stock_receipt_id=stock_receipt.id)

    else:
        context = {'stock_receipt': stock_receipt}
        return render(request, 'StockEntry_withPO_edit.html', context)
   
   


def stock_receipt_detail(request, stock_receipt_id):
    stock_receipt = get_object_or_404(Stock_Receipt, id=stock_receipt_id)

    context = {'stock_receipt': stock_receipt}
    return render(request, 'stock_receipt_detail.html', context)

def show_stock_receipts(request):
    print("display_stock_receipts view called") 
    branches = Branch.objects.all()
    ingredients = Ingredient.objects.all()
    stock_receipts = Stock_Receipt.objects.all()
    purchase_orders = Purchase_Order.objects.all()  # Retrieve all purchase orders
    context = {
        'branches': branches,
        'ingredients': ingredients,
        'stock_receipts': stock_receipts,
        'purchase_orders': purchase_orders,  # Include purchase orders in context
    }
    return render(request, 'show_stock_receipts.html', context)






# def get_items(request):
#     branch_id = request.GET.get('branch_id')
#     items = stockbalanceCreate.objects.filter(branch_id=branch_id)
#     item_list = []

#     for item in items:
#         item_data = {
#             'id': item.id,
#             'item_name': item.item.item_name
#         }
#         item_list.append(item_data)

#     return JsonResponse({'items': item_list})



# def StockEntry_withoutPO(request):
#     form = Stock_ReceiptForm()
#     uoms = UOM.objects.all()
#     suppliers = Supplier.objects.all()
#     branches = Branch.objects.all()

#     if request.method == "POST":
#         receive_by = request.POST.get("receive_by")
#         supplier = Supplier.objects.get(id=request.POST.get("mainItem"))
#         branch_id = request.POST.get("branch")
#         branch = Branch.objects.get(id=branch_id)

#         # Get the data from the POST request after obtaining branch and other details
#         ingredients_list = list(request.POST.getlist("ingredient"))
#         uom_list = list(request.POST.getlist("mainUOM"))
#         quantity_list = list(request.POST.getlist("quantity"))
#         unitprices_list = request.POST.getlist('unit_price')

#         new_Purchase_Order = Stock_Receipt.objects.create(
#             supplier=supplier, receive_by=receive_by, branch_name=branch
#         )

#         for i in range(len(ingredients_list)):
#             ingredient_id = int(ingredients_list[i])
#             uom = UOM.objects.get(id=int(uom_list[i]))
#             quantity = int(quantity_list[i])
#             unit_price = Decimal(unitprices_list[i])

#             # Use the branch_name field to filter ingredients associated with the selected branch
#             ingredient = stockbalanceCreate.objects.filter(branch=branch, item__id=ingredient_id).first()
#             if ingredient is None:
#                 continue

#             print("quantity before:", ingredient.item_quantity)
#             item_quantity = ingredient.item_quantity + quantity
#             print("quantity after:", item_quantity)
#             ingredient.item_quantity = item_quantity
#             ingredient.save()

#             ingredient.receveive_quantity = quantity

#             total_price = Decimal(unit_price) * quantity
#             newStockReceip_withoutPO = Ingredient.objects.create(
#             item=ingredient, item_UOM=uom, quantity=quantity,
#             total_price=total_price, unit_price=unit_price
#            )


#             print("quantity after:", item_quantity)
#             newStockReceip_withoutPO.main_item = new_Purchase_Order.item

#             newStockReceip_withoutPO.item.save()

#             new_Purchase_Order.ingredients.add(newStockReceip_withoutPO)

#         return redirect("show_stock_receipts")

#     context = {
#         "form": form,
#         "uoms": uoms,
#         "suppliers": suppliers,
#         "branches": branches,
#     }

#     return render(request, 'StockEntry_withoutPO.html', context)

def update_purchase(request, po_number):
    purchase_order = get_object_or_404(Purchase_Order, po_number=po_number)
    items = Item.objects.all()
    uoms = UOM.objects.all()
    suppliers = Supplier.objects.all()
    branches = Branch.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("mainItem")
        supplier = Supplier.objects.get(id=supplier_id)
        branch_id = request.POST.get("branch")
        branch = Branch.objects.get(id=branch_id)
        ingredients_list = list(request.POST.getlist("ingredient"))
        uom_list = list(request.POST.getlist("mainUOM"))
        quantity_list = list(request.POST.getlist("quantity"))
        unit_price_list = list(request.POST.getlist("unit_price"))
        
        purchase_order.supplier = supplier
        purchase_order.branch_name = branch
        purchase_order.ingredients.all().delete()  # Clear existing ingredients
        
        for i in range(len(ingredients_list)):
            ingredient = Item.objects.get(id=int(ingredients_list[i]))
            uom = UOM.objects.get(id=int(uom_list[i]))
            quantity = int(quantity_list[i])
            unit_price = float(unit_price_list[i])
            new_ingredient = Ingredient.objects.create(
                main_item=ingredient, item=ingredient, item_UOM=uom, quantity=quantity, unit_price=unit_price
            )
            purchase_order.ingredients.add(new_ingredient)
        
        purchase_order.save()
        messages.success(request, "Successfully updated purchase order")
        return redirect("/show_purchase_order")
    else:
        form = Purchase_OrderForm()

    context = {
        "purchase_order": purchase_order,
        "items": items,
        "uoms": uoms,
        "suppliers": suppliers,
        "branches": branches,
    }
    return render(request, "update_purchase.html", context)





#get item assign to branch



# calculate overdue days
def calculate_overdue_days(purchase_date, supplier):
    today = timezone.now().date()

    # Handling offset-naive and offset-aware datetime objects
    if timezone.is_aware(purchase_date):
        purchase_date = purchase_date.date()

    due_date = purchase_date + timedelta(days=supplier.credit_days)
    overdue_days = (today - due_date).days

    return overdue_days



def Purchases(request):
    purchase_orders = Stock_Receipt.objects.all()

    for order in purchase_orders:
        order.overdue_days = calculate_overdue_days(order.purchase_date, order.supplier)
        
        

    return render(request, 'Purchases.html', {'purchase_orders': purchase_orders})


def show_stock_receipts(request):
    # Retrieve the list of stock receipts and their ingredients
    purchase_orders = Stock_Receipt.objects.all()

    context = {
        'purchase_orders': purchase_orders,
    }

    return render(request, 'show_stock_receipts.html', context)



# def show_stock_receipts(request):
#     purchase_orders = Stock_Receipt.objects.all()
#     return render(request, 'show_stock_receipts.html', {'purchase_orders': purchase_orders})

def manage_payments(request):
    purchase_orders = Stock_Receipt.objects.all().annotate(total_sumed_prices=Sum("ingredients__total_price"))
    return render(request, 'manage_payments.html', {'purchase_orders': purchase_orders})

    

def viewdetail(request, po_number):
    queryset = Purchase_Order.objects.filter(po_number=po_number)
    context = {
        "purchasedetails": queryset,
    }
    return render(request, "view_eachpurchase.html", context)









def show_purchase_order(request):
    purchases = Purchase_Order.objects.all()
    context = {"purchases": purchases}
    return render(request, "show_purchase_order.html", context)


#get branch items
def get_branch_items(request):
    branch_id = request.GET.get('branch_id')
    print("Received branch_id:", branch_id)  # Debug statement
    try:
        branch = Branch.objects.get(id=branch_id)
        items = Item.objects.filter(branch_name=branch)
        data = {
            'items': [
                {'id': item.id, 'item_name': item.item_name} for item in items
            ]
        }
        return JsonResponse(data)
    except Branch.DoesNotExist:
        print("Branch not found in the database.")  # Debug statement
        return JsonResponse({'error': 'Branch not found.'}, status=400)



# add_purchase 

def add_purchase_order(request):
    form = Purchase_OrderForm()
    items = Item.objects.all()
    uoms = UOM.objects.all()
    suppliers = Supplier.objects.all()
    branches = Branch.objects.all()

    if request.method == "POST":
        supplier_id = request.POST.get("mainItem")
        supplier = Supplier.objects.get(id=supplier_id)
        branch_id = request.POST.get("branch")
        branch = Branch.objects.get(id=branch_id)
        ingredients_list = list(request.POST.getlist("ingredient"))
        uom_list = list(request.POST.getlist("mainUOM"))
        quantity_list = list(request.POST.getlist("quantity"))
        
        new_Purchase_Order = Purchase_Order.objects.create(supplier=supplier, branch_name=branch)
        
        for i in range(len(ingredients_list)):
            ingredient = Item.objects.get(id=int(ingredients_list[i]))
            uom = UOM.objects.get(id=int(uom_list[i]))
            quantity = int(quantity_list[i])
            new_ingredient = Ingredient.objects.create(
                main_item=ingredient, item=ingredient, item_UOM=uom, quantity=quantity
            )
            new_Purchase_Order.ingredients.add(new_ingredient)    
        return redirect("show_purchase_order")
        
    else:
        form = Purchase_OrderForm()

    context = {
        "form": form,
        "items": items,
        "uoms": uoms,
        "suppliers": suppliers,
        "branches": branches,
    }
    return render(request, "add_purchase_order.html", context)








#delete_purchase
def deletepurchase(request, po_number):
    queryset = Purchase_Order.objects.get(po_number=po_number)
    if request.method == "POST":
        queryset.delete()
        return redirect(
            "show_purchase_order"
        )  
    return render(request, "deletepurchaseorder.html")




def search_single_PO(request, pk):
    return render(request, "")


# Confirmed POs
def confirm_po(request):
    return render(request, "")


def get_connected_supplier(request, supplier_id):
    supplier = Supplier.objects.get(id=supplier_id)
    connected_suppliers = supplier.connected_suppliers.all()
    supplier_list = [{"id": i.id, "name": i.name} for i in connected_suppliers]
    return JsonResponse(request, {"suppliers": supplier_list})




def confirm_stock_transfer(request):
    if request.method == "POST":
        po_number = request.POST.get("po_number", None)
        stock = Stock_Receipt.objects.filter(po_number=po_number).first()

        context = {"stock": stock}

        return render(request, "confirm_stock_transfer.html", context)

    return render(request, "confirm_stock_transfer.html")


# To View Stocks
def view_stock(request):
    stocks = Stock_Receipt.objects.all()
    context = {"stocks": stocks}
    return render(request, "view_stock.html", context)


# To add request Stock
def stock_request(request):
    form = StockRequestForm()
    items = Item.objects.all()
    uoms = UOM.objects.all()
    orders = StockRequest.objects.all()

    if request.method == "POST":

        form = StockRequestForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("view_stock_request")
            except:
                pass
    else:
        form = StockRequestForm()

    context = {
        "form": form,
        "items": items,
        "uoms": uoms,
        "orders": orders,
    }
    return render(request, "stock_request.html", context)


# To View Stocks request
def view_stock_request(request):
    requests = StockRequest.objects.all()
    context = {"requests": requests}
    return render(request, "view_stock_request.html", context)

def show_stockreceip(request):
    header = 'list of items'
    form = Purchase_OrdeSearchForm(request.POST or None)
    queryset = Purchase_Order.objects.all()
    context={
        "header": header,
        "queryset": queryset,
        "form": form,
    }
    if request.method == "POST":
        queryset = Purchase_Order.objects.filter(
                                        po_number__icontains= form['po_number'].value())    
        context={
        "form": form,
        "header":header,
        "queryset": queryset,
    }
    return render(request, "stockentry.html", context) 

# To Add Stock Entry


# To View Stock Entry
def view_stock_entry(request):
    entries = StockEntry.objects.all()
    print(entries)
    context = {"entries": entries}

    return render(request, "view_stock_entry.html", context)


# To add billed stock
def billed_stock(request):
    form = BilledStockForm()
    items = Item.objects.all()
    uoms = UOM.objects.all()
    if request.method == "POST":
        form = BilledStockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("view_billed_stock")
    else:
        form = BilledStockForm()
    return render(
        request, "billed_stock.html", {"form": form, "items": items, "uoms": uoms}
    )


# To view billed stock
def view_billed_stock(request):
    bills = BilledStock.objects.all()
    context = {"bills": bills}
    return render(request, "view_billed_stock.html", context)

#branch transfer 



def fetch_items(request):
    branch_id = request.GET.get('branch_id')
    items = Item.objects.filter(branch__id=branch_id)
    item_list = []

    for item in items:
        item_data = {
            'id': item.id,
            'item_name': item.item_name
        }
        item_list.append(item_data)

    return JsonResponse(item_list, safe=False)




# get branch items
def get_items_for_branch(request):
    branch_id = request.GET.get('branch_id')
    items = stockbalanceCreate.objects.filter(branch_id=branch_id)
    item_list = []

    for item in items:
        item_data = {
            'id': item.id,
            'item_name': item.item.item_name
        }
        item_list.append(item_data)

    return JsonResponse({'items': item_list})



def transfer_items(request):
    branches = Branch.objects.all()
    items = Item.objects.all()

    if request.method == 'POST':
        from_branch_id = request.POST.get('from_branch')
        to_branch_id = request.POST.get('to_branch')

        item_ids = request.POST.getlist('item')
        quantities = request.POST.getlist('quantity')

        from_branch = Branch.objects.get(pk=from_branch_id)
        to_branch = Branch.objects.get(pk=to_branch_id)

        insufficient_items = []  # A list to store insufficient items

        with transaction.atomic():
            for item_id, quantity in zip(item_ids, quantities):
                item = Item.objects.get(pk=item_id)
                quantity = int(quantity)

                # Check if the from_branch has enough quantity of the item
                from_branch_item = stockbalanceCreate.objects.get_or_create(branch=from_branch, item=item)[0]
                if from_branch_item.item_quantity < quantity:
                    insufficient_items.append(item.item_name)
                else:
                    # Perform the quantity update only if there are enough items in the from_branch
                    from_branch_item.item_quantity -= quantity
                    from_branch_item.save()

                    # Update to_branch quantity
                    to_branch_item = stockbalanceCreate.objects.get_or_create(branch=to_branch, item=item)[0]
                    to_branch_item.item_quantity += quantity
                    to_branch_item.save()

                    # Create BranchTransfer record
                    BranchTransfer.objects.create(from_branch=from_branch, to_branch=to_branch, item=item, quantity=quantity)

            if insufficient_items:
                # Display a message for insufficient items
                items_message = ", ".join(insufficient_items)
                messages.error(request, f"The following items are insufficient: {items_message}")
            else:
                messages.success(request, "Items transferred successfully.")
                return redirect('branch_transfer_items')

    return render(request, 'transfer_items.html', {'branches': branches, 'items': items})



def branch_transfer_items(request):
    transfers = BranchTransfer.objects.all()
    context = {
        'transfers': transfers
    }
    return render(request, 'show_branch_transfers.html', context)





# Add_item_group
def item_group(request):
    if request.method == "POST":
        form = ItemGroupForm(request.POST)
        group_code = generate_itemgroup_code()
        if form.is_valid():
            try:
                new_itemgroup = form.save(commit = False)
                new_itemgroup.group_code = group_code
                new_itemgroup.save()
                return redirect("view_item_group")
            except:
                pass
    else:
        form = ItemGroupForm()

    context = {"form": form}
    return render(request, "item_group.html", context)


#view_item_group
def view_item_group(request):
    Item_groups = Item_group.objects.all()
    print(Item_groups)
    context = {"Item_groups": Item_groups}
    return render(request, "view_item_group.html", context)

 
#add_item_category
def item_category(request):
    if request.method == "POST":
        form = ItemCategoryForm(request.POST)
        category_code = generate_itemcategory()
        if form.is_valid():
            try:
                new_po = form.save(commit=False)
                new_po.category_code = category_code
                new_po.save()
                return redirect("view_item_category")
            except:
                pass
    else:
        form = ItemCategoryForm()

    context = {"form": form}
    return render(request, "item_category.html", context)


# view_item_category
def view_item_category(request):
    Item_categories = Item_category.objects.all()
    context = {"Item_categories": Item_categories}
    return render(request, "view_item_category.html", context)

#item issue and updates

#end of items

# add_bom 
def bom(request):
    form = BOMForm()
    items = Item.objects.all()
    uoms = UOM.objects.all()
    if request.method == "POST":
        item = Item.objects.get(id=request.POST.get("mainItem"))
        ingredients_list = list(request.POST.getlist("ingredient"))
        uom_list = list(request.POST.getlist("mainUOM"))
        quantity_list = list(request.POST.getlist("quantity"))

        new_BOM = BOM.objects.create(item=item)

        for i in range(len(ingredients_list)):
            ingredient = Item.objects.get(id=int(ingredients_list[i]))
            uom = UOM.objects.get(id=int(uom_list[i]))
            quantity = int(quantity_list[i])
            new_ingredient = Ingredient.objects.create(
                main_item=item, item=ingredient, item_UOM=uom, quantity=quantity
            )
            new_BOM.ingredients.add(new_ingredient)
        return redirect("view_bom")
    else:
        form = BOMForm()

    context = {
        "form": form,
        "items": items,
        "uoms": uoms,
    }
    return render(request, "bom.html", context)


def view_bom(request):
    boms = BOM.objects.all()
    context = {"boms": boms}
    return render(request, "view_bom.html", context)


# view bom colum
def view_bom_detail(request, bom_id):
    queryset = BOM.objects.filter(bom_id=bom_id)
    context = {
        "bomss": queryset,
    }
    return render(request, "view_eachbom.html", context)


def deletebom(request, id):
    queryset = BOM.objects.get(id=id)
    if request.method == "POST":
        queryset.delete()
        return redirect(
            "view_bom"
        )  # redirect to a new page after saving to avoid dublicate of data when save
    return render(request, "deleteitems.html")


def view_branchtranfer(request):
    branchese = BranchTransfer.objects.all()
    print(branchese)
    context = {"brancheses": branchese}
    return render(request, "view_stocktransfer.html", context)


# Add Company Details
def add_company_details(request):
    form = Company_detailsForm()
    company_code = generate_company_code()
    if request.method == "POST":
        form = Company_detailsForm(request.POST)
        company_code = generate_company_code()
        if form.is_valid():
            new_po = form.save(commit=False)
            new_po.company_code = company_code
            new_po.save()
            form.save()
            return redirect("company_details")
        else:
            messages.info(request, message="Could not save company details")
            return redirect("company_details")

    context = {"form": form}

    return render(request, "add_company_details.html", context)



# View Company Details
def company_details(request):
    company_details = Company_details.objects.all()
    context = {"company_details": company_details}
    return render(request, "company_details.html", context)


# Add Branch
def branch(request):
    form = BranchForm()
    branch_code = generate_Branch_code ()
    if request.method == "POST":
        form = BranchForm(request.POST)
        branch_code = generate_Branch_code ()
        if form.is_valid():
            newbranch_code = form.save(commit=False)
            newbranch_code.branch_code = branch_code
            newbranch_code.save()
            form.save()
            return redirect("show_branch")
        else:
            messages.info(request, message="Could not save branch")
            return redirect("branch")

    context = {"form": form}

    return render(request, "branch.html", context)


# View Branch
def show_branch(request):
    branches = Branch.objects.all()
    print(branches)
    context = {"branches": branches}
    return render(request, "show_branch.html", context)


# View UoM
def UoM(request):
    uom = UOM.objects.all()
    print(uom)
    context = {"uom": uom}
    return render(request, "UoM.html", context)


# List of Items
def list_of_items(request):
    items = Item.objects.all()
    print(items)
    context = {"items": items}
    return render(request, "list_of_items.html", context)


def request_payment(
    request, purchase_order_no, suppliername, phonenumber="254711123120"
):
    URL = BASE_URL + "purchase-order/"
    purchases = requests.get(
        URL, headers={"Accept": "application/json", "Content-Type": "application/json"}
    )

    URL = "http://bharathbrandsdotin.pythonanywhere.com/api/services/"
    data = {
        "service_id": "ST0033",
        "service_description": "Request Alada Payment",
        "total_fees": 100.0,
        "channel_id": "webfev011-2",
        "user_id": "1",
        "national_id": "232298",
        "phone_number": phonenumber,
        "service_type": "DirectServicePayment",
        "input_params_values": {
            "purchase_order_no": purchase_order_no,
            "supplier_name": suppliername,
            "total_fees": 100.0,
        },
    }
    response = requests.post(
        URL,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        data=json.dumps(data),
    )
    print(response.json())
    return redirect("manage_payments")


def loginPage(request):
    service_fields = get_service_fields("Login")
    service_metadata = get_service_metadata("Registration")
    National_ID = int("67889")
    if request.method == "POST":
        request.session["national_id"] = int("67889")
        # request.session['national_id']=request.POST.get('National_ID')
        National_ID = request.session["national_id"]
        data = request.POST
        print(data)
        request.session["captured_data"] = data
        print("login")
        response = transaction_login(data)
        if response == "AuthenticationFailed":
            print("response ", response)
            messages.error(request, "Invalid Credentials..!!")
            return redirect("loginPage")

        else:
            print("response ", response)
            return redirect("show_branch")
    captured_data = request.session.get("captured_data")
    # print("captured_data ", captured_data)
    context = {
        "service_fields": service_fields["service_fields"],
        "service_metadata": service_metadata,
        "National_ID": National_ID,
        "captured_data": captured_data,
    }
    return render(request, "login.html", context)


# Register
def registerPage(request):
    service_fields = get_service_fields("Registration")
    service_metadata = get_service_metadata("Registration")
    if request.method == "POST":
        data = request.POST
        response = all_transaction_process(data)  # calling transaction module
        if response == "failed":
            # print('Response ', response)
            messages.error(request, "please enter correct details")
            return redirect("registerPage")
        else:
            print("Response ", response)
            messages.success(request, "Please Login And Proceed Ahead..!!")
            return redirect("loginPage")
    context = {
        "service_fields": service_fields["service_fields"],
        "service_metadata": service_metadata,
    }
    return render(request, "register.html", context)


# logout
def logoutUser(request):
    logout(request)
    return redirect("home")


@login_required
def profile(request):
    return redirect("")


# SUPPLIER VIEWS
def supplier_mode(request):
    if request.session["mode"] == "supplier":
        request.session["mode"] = "client"
    elif request.session["mode"] == "client":
        request.session["mode"] = "supplier"
    return redirect("home")


# POS
def pos(request):
    return render(request, "pos.html")


def get_suppliers():
    # Make the API call
    url = "http://bharathbrandsdotin.pythonanywhere.com/api-alada/register-supplier/"
    response = requests.get(url)

    if response.status_code == 200:
        # Extract the JSON response
        suppliers = response.json()
        return suppliers
    else:
        # Handle API error
        return []


def my_view(request):
    # Call the get_suppliers() function to fetch the list of suppliers
    suppliers = get_suppliers()

    # Pass the list of suppliers to the template context
    context = {"suppliers": suppliers}

    return render(request, "my_template.html", context)


# payment


# def pay(request):
#     cl = MpesaClient()
#     phone_number = 07189023456
#     cl.process_payment(phone_number, amount=100)
#     phone_number = "0718908494"
#     amount = 1
#     account_reference = "reference"
#     transaction_desc = "Description"
#     callback_url = "https://api.darajambili.com/express-payment"
#     response = cl.stk_push(
#         phone_number, amount, account_reference, transaction_desc, callback_url
#     )
#     return HttpResponse(response)

def pay(request, id):
    cl = MpesaClient()
    
    po = Stock_Receipt.objects.annotate(total_sumed_prices=Sum("ingredients__total_price")).filter(pk=id).first()
    
    phone_number = "0700805271"
    amount = int(po.total_sumed_prices)
    account_reference = "reference"
    transaction_desc = "Description"
    callback_url = "https://api.darajambili.com/express-payment"

    # Initiate the payment process using the MpesaClient
    response = cl.stk_push(
        phone_number, amount, account_reference, transaction_desc, callback_url
    )

    return HttpResponse(response)

# Daraja view
def stk_push_callback(request):
    data = request.body
    return HttpResponse("STK Push in Django")
