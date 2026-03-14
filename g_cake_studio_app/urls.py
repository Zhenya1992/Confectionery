from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/count/', views.cart_api_count, name='cart_api_count'),
    path('api/cart/add/<int:product_id>/', views.cart_api_add, name='cart_api_add'),
    path('reviews/', views.reviews, name='reviews'),
    path('order/', views.order_view, name='order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_history, name='order_history'),
    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('check-telegram-auth/', views.check_telegram_auth, name='check_telegram_auth'),
]