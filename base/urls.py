from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home_url'),
    path('shoes/', views.shoes, name='shoes_url'),
    path('perfumes/', views.perfumes, name='perfumes_url'),
    path('makeup/', views.makeup, name='makeup_url'),
    path('skincare/', views.skincare, name='skincare_url'),
    path('collections/', views.collections, name='collections_url'),
    path('about/', views.about_view, name='about_url'),
    path('auth/', views.auth_view, name='auth_url'),
    path('logout/', views.logout_view, name='logout_url'),
    path('search/', views.search_results, name='search_url'),
    path('cart/', views.cart_view, name='cart_url'),
    path('product/<int:id>/', views.product_detail, name='product_url'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart_url'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart_url'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_url'),
]