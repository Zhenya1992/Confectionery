from django.core.cache import cache
import os
import requests
import uuid
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import json
import random
from .models import Product, Review, CartItem, Order, OrderItem, TelegramAuthToken
from .forms import OrderForm, ReviewForm
from dotenv import load_dotenv


load_dotenv()

def home(request):
    """Главная страница"""
    return render(request, 'confectionery/home.html')


class ProductListView(ListView):
    """Список товаров"""
    model = Product
    template_name = 'confectionery/products.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(is_available=True).order_by('created_at')


def product_detail(request, pk):
    """Детальная страница товара"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'confectionery/product_detail.html', {'product': product})


def about(request):
    """Страница О нас"""
    return render(request, 'confectionery/about.html', {
        'title': 'О нашей кондитерской',
    })


def custom_404_view(request, exception):
    """Кастомная страница 404"""
    return render(request, 'confectionery/404.html', status=404)


def login_view(request):
    """Авторизация пользователя"""

    if 'telegram_token' not in request.session:
        request.session['telegram_token'] = str(uuid.uuid4())

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'confectionery/login.html')


def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    return render(request, 'confectionery/register.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def cart_view(request):
    """Просмотр корзины"""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    total = sum(item.product.price * item.quantity for item in cart_items)
    total_quantity = sum(item.quantity for item in cart_items)

    return render(request, 'confectionery/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'total_quantity': total_quantity,
    })

@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину (обычный POST)"""
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} добавлен в корзину.')
    next_url = request.META.get('HTTP_REFERER', 'product_list')
    return redirect(next_url)


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} удален из корзины.')
    return redirect('cart')


@login_required
def cart_api_count(request):
    """API: получить количество товаров в корзине"""
    try:
        count = CartItem.objects.filter(user=request.user).count()
        return JsonResponse({'count': count, 'success': True})
    except Exception as e:
        return JsonResponse({'count': 0, 'success': False, 'error': str(e)})


@login_required
@require_POST
def cart_api_add(request, product_id):
    """API: добавить товар в корзину (JSON)"""
    try:
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            user=request.user,
            defaults={'quantity': 1}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        count = CartItem.objects.filter(user=request.user).count()

        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'{product.name} добавлен в корзину'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def reviews(request):
    """Страница отзывов - только для авторизованных"""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        rating = int(request.POST.get('rating', 5))
        if not text:
            messages.error(request, 'Пожалуйста, введите текст отзыва.')
        else:
            Review.objects.create(
                author=request.user.username,
                text=text,
                rating=rating
            )
            messages.success(request, 'Ваш отзыв отправлен.')
            return redirect('reviews')

    reviews_list = Review.objects.all().order_by('-created_at')
    return render(request, 'confectionery/reviews.html', {
        'reviews': reviews_list,
        'title': 'Отзывы наших клиентов'
    })


@login_required
def order_view(request):
    """Оформление заказа"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f"ORD-{random.randint(100000, 999999)}"
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart_items.delete()
            messages.success(request, f'Заказ #{order.order_number} успешно оформлен!')
            return redirect('order_success', order_id=order.id)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = OrderForm()

    return render(request, 'confectionery/order.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })


@login_required
def order_success(request, order_id):
    """Страница успешного заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confectionery/order_success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'confectionery/order_detail.html', {'order': order})


@login_required
def order_history(request):
    """История заказов"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'confectionery/order_history.html', {'orders': orders})

@login_required
@require_POST
def update_cart_quantity(request, item_id):
    action = request.POST.get('action')
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart')


def generate_telegram_token():
    return str(uuid.uuid4())


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message")
            if message:
                text = message.get("text")
                chat = message.get("chat")
                user_id = chat.get("id")
                username = chat.get("username") or f"tg_{user_id}"

                print(f"Message from {username}: {text}")

                if text == "/start":
                    user, created = User.objects.get_or_create(username=username)
                    token = str(uuid.uuid4())
                    cache.set(f"tg_auth_{token}", user.id, timeout=300)  # 5 минут
                    link = f"https://forty-queens-learn.loca.lt/check-telegram-auth/?token={token}"
                    send_message(user_id, f"Привет! Войдите на сайт по ссылке:\n{link}")

        except Exception as e:
            print("Webhook error:", e)

    return JsonResponse({"ok": True})


def check_telegram_auth(request):
    token = request.GET.get("token")

    if not token:
        return redirect("login")

    try:
        auth_token = TelegramAuthToken.objects.get(token=token)
        user = auth_token.user
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        auth_token.delete()
        return redirect("home")

    except TelegramAuthToken.DoesNotExist:
        return redirect("login")

def telegram_callback(request):
    token = str(uuid.uuid4())
    return redirect(f'/check-telegram-auth/?token={token}')

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    r = requests.post(url, json=payload)
    print("Send message response:", r.json())

