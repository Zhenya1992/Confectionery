from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from g_cake_studio_app import views
from g_cake_studio_app.views import ProductListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('about/', views.about, name='about'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('telegram_callback/', views.telegram_callback, name='telegram_callback'),
    path('telegram_webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('check-telegram-auth/', views.check_telegram_auth, name='check_telegram_auth'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/count/', views.cart_api_count, name='cart_api_count'),
    path('api/cart/add/<int:product_id>/', views.cart_api_add, name='cart_api_add'),
    path('reviews/', views.reviews, name='reviews'),
    path('order/', views.order_view, name='order'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('order/history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='confectionery/password_reset.html',
        email_template_name='confectionery/password_reset_email.html',
        subject_template_name='confectionery/password_reset_subject.txt'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='confectionery/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='confectionery/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='confectionery/password_reset_complete.html'),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'g_cake_studio_app.views.custom_404_view'