
from django.urls import path
from . import views

urlpatterns = [
    path('admin/orders/', views.orders_list, name='admin_orders'),
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    path('update_cart_quantity/<int:product_id>/<int:qty>/', views.update_cart_quantity,
        name='update_cart_quantity'),

    path('checkout/', views.checkout, name='checkout'),
    path("order-confirmation/<int:order_id>/", views.order_confirmation, name="order_confirmation"),


    path('offers/', views.offers, name='offers'),
    
    path('products/add/', views.add_product, name='add_product'),
    path("products/delete/<int:id>/", views.delete_product, name="delete_product"),
    path("products/edit/<int:id>/", views.edit_product, name="edit_product"),


    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
]


