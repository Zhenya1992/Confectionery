from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from g_cake_studio_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('g_cake_studio_app.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='confectionery/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'g_cake_studio_app.views.custom_404_view'