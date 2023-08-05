from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
   
    # supplier
    path("add-supplier-type", views.add_supplier_type, name="add_supplier_type"),
    path("show-supplier-type", views.show_supplier_type, name="show_supplier_type"),
    path("edit-supplier-type", views.edit_supplier_type, name="edit_supplier_type"),
    path("add-supplier", views.add_supplier, name="add_supplier"),
    path("suppliers", views.views_suppliers, name="views_suppliers"),
    # Product
    path("add-product", views.add_product, name="add_product"),
    path("show_product", views.show_product, name="show_product"),
    path("add_stocks_balance", views.add_stocks_balance, name="add_stocks_balance"),
    path("stocks_balance", views.stocks_balance, name="stocks_balance"),
    path('edit_stocks_balance/<int:id>/', views.edit_stocks_balance, name='edit_stocks_balance'),

    path("edit-product/<int:item_id>", views.edit_product, name="edit_product"),
    path("list-of-items", views.list_of_items, name="list_of_items"),
    path("api/supplier/<int:supplier_id>/",views.get_connected_supplier,name="get_connected_supplier"),
    
    # #  Purchase Order
    path('get_items/', views.get_items, name='get_items'),
    path('fetch_items/', views.fetch_items, name='fetch_items'),
    
    path("deletepurchase/<str:po_number>/", views.deletepurchase, name="deletepurchase"),
    path('StockEntry_withoutPO',views.StockEntry_withoutPO, name='StockEntry_withoutPO'),
    path('StockEntry_withPO',views.StockEntry_withPO, name='StockEntry_withPO'),
    # path('StockEntry_withPO2',views.StockEntry_withPO2, name='StockEntry_withPO2'),

    path('edit_purchase_order/<int:purchase_order_id>/', views.edit_purchase_order, name='edit_purchase_order'),
    
    path('display_purchase_orders/', views.display_purchase_orders, name='display_purchase_orders'),
   


    
    path('StockEntry_withPO_edit/<int:stock_receipt_id>/', views.StockEntry_withPO_edit, name='StockEntry_withPO_edit'),
    path('get_purchase_order_data/', views.get_purchase_order_data, name='get_purchase_order_data'),
    # path('create_purchase_order',views.create_purchase_order, name='create_purchase_order'),
    path("show_purchase_order", views.show_purchase_order, name="show_purchase_order"),
    path("Purchases", views.Purchases, name="Purchases"),
    
    # path('update_items/<str:po_number>/', views.update_items, name='update_items'),
    path('update_purchase/<str:po_number>/', views.update_purchase, name='update_purchase'),

    # # path('add_quantity/<str:po_number>/', views.add_quantity, name='add_quantity'),
    # path('purchase_order_detail/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    



        
    path("viewdetail/<str:po_number>", views.viewdetail, name="viewdetail"),
    # path("add_purchase", views.add_purchase, name="add_purchase"),
    path("add_purchase_order", views.add_purchase_order, name="add_purchase_order"),
    path('get_branch_items/', views.get_branch_items, name='get_branch_items'),
    # path("show_purchase", views.show_purchase, name="show_purchase"),
  
    path("search-single-po/<pk>/", views.search_single_PO, name="search_single_PO"),
    
    path("confirm-po/<pk>/", views.confirm_po, name="confirm_po"),
    # path('update_items/<str:po_number>/', views.updatepurchase, name='update_items'),
    path("show_stockreceip", views.show_stockreceip, name="show_stockreceip"),
    
    # Homepage
    path("", views.home, name="home"),
    # register/login/logout
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="registration/logout.html"),
        name="logout",
    ),
    # Authentication
    path("login/", views.loginPage, name="loginPage"),
    path("register/", views.registerPage, name="registerPage"),
    path("logout/", views.logoutUser, name="logout"),
    path("profile/", views.profile, name="profile"),
    # inbuilt login path
    # path("accounts/", include("django.contrib.auth.urls")),
    # To Confirm Stock Transfer
   
    path("view-stock", views.view_stock, name="view_stock"),
    path("show_stock_receipts", views.show_stock_receipts, name="show_stock_receipts"),
    
    path('show_stock_receipts2/<int:stock_receipt_id>/', views.show_stock_receipts2, name='show_stock_receipts2'),
    #  stock_receipt_detail
    path('stock_receipt_detail/<int:stock_receipt_id>/', views.stock_receipt_detail, name='stock_receipt_detail'),
    path('stocks_balance/edit/<str:item_id>/', views.edit_stocks_balance, name='edit_stocks_balance'),

    
    path("stock-request", views.stock_request, name="stock_request"),
    path("view-stock-request", views.view_stock_request, name="view_stock_request"),
    path("view-stock-entry", views.view_stock_entry, name="view_stock_entry"),
    path("billed-stock", views.billed_stock, name="billed_stock"),
    path("view-billed-stock", views.view_billed_stock, name="view_billed_stock"),
    # branch transfer
    path('transfer_items', views.transfer_items, name='transfer_items'),
    # path('get_item_uoms/', views.get_item_uoms, name='get_item_uoms'),
    path('get_items_for_branch/', views.get_items_for_branch, name='get_items_for_branch'),
    path('branch_transfer_items/', views.branch_transfer_items, name='branch_transfer_items'),


    
    path("view-branch", views.view_branchtranfer, name="viewbranch"),
    path("confirm-stock-transfer", views.confirm_stock_transfer, name="confirm_stock_transfer",),
    # Payments
    path("manage-payments", views.manage_payments, name="manage_payments"),
    path("pay/<int:id>", views.pay, name="pay"),
    path("daraja/stk_push", views.stk_push_callback, name="stk_push_callback"),
    
    
    # Item category
    path("item-category", views.item_category, name="item_category"),
    path("view-item-category", views.view_item_category, name="view_item_category"),
    # Item group
    path("item-group", views.item_group, name="item_group"),
    path("view-item-group", views.view_item_group, name="view_item_group"),
    # BOM
    path("deletebom/<int:id>/", views.deletebom, name="deletebom"),
    path("bom", views.bom, name="bom"),
    path("view-bom", views.view_bom, name="view_bom"),
    path("view-bom/<str:bom_id>", views.view_bom_detail, name="view_bom_detail"),
    # Company Details
    path("add-company-details", views.add_company_details, name="add_company_details"),
    path("company-details", views.company_details, name="company_details"),
    # Branch
    path("branch", views.branch, name="branch"),
    path("show-branch", views.show_branch, name="show_branch"),
    # UoM
    path("UoM", views.UoM, name="UoM"),
    # Request Payment
    path(
        "request-payment/<int:purchase_order_no>/<str:suppliername>/<str:phonenumber>",
        views.request_payment,
        name="request_payment",
    ),
    # Supplier mode
    path("supplier-mode", views.supplier_mode, name="supplier_mode"),
    # POS
    path("pos/", views.pos, name="pos"),
]
# for Media Storage
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
