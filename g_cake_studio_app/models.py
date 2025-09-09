from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Product(models.Model):
    """Класс моделей продуктов"""

    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    main_image = models.ImageField('Главное изображение', upload_to='products/', blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True)
    is_available = models.BooleanField('Доступен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

class ProductImage(models.Model):
    """Класс модели для изображений продуктов"""

    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

class Review(models.Model):
    """Класс моделей отзывов"""

    author = models.CharField('Автор', max_length=100)
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Оценка', default=5)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.author}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']


class CartItem(models.Model):
    """Класс модели для элементов корзины"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=1)
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'


class Order(models.Model):
    """Класс моделей для заказов"""

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Банковская карта'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Пользователь")
    order_number = models.CharField("Номер заказа", max_length=20, unique=True, default="TEMP")
    name = models.CharField("ФИО", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    address = models.TextField("Адрес доставки")
    delivery_time = models.CharField("Время доставки", max_length=100, blank=True)
    comments = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Дата заказа", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    payment_method = models.CharField("Способ оплаты", max_length=20, choices=PAYMENT_METHODS, default='cash')
    is_paid = models.BooleanField("Оплачен", default=False)

    def __str__(self):
        return f"Заказ #{self.order_number}"

    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    """Класс моделей для элементов заказа"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Продукт")
    quantity = models.PositiveIntegerField("Количество", default=1)
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"
