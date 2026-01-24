from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# -------------------------
# المنتجات
# -------------------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    category = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "المنتجات "



    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
   
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم القيد الجامعي"
    )

    full_name = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
  
    class Meta:
        verbose_name_plural = "الملف الشخصي"
        
    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


# -------------------------
# الطلبات
# -------------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', ' الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغى'),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    full_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=50)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    
    
    class Meta:
        verbose_name_plural = "الطلبات"


    def __str__(self):
        return f"طلب #{self.id} — {self.full_name}"


# -------------------------
# عناصر الطلب
# -------------------------
class OrderItem(models.Model):                                                         # Many 
    order = models.ForeignKey(
        Order,                                                         # One
        related_name='items',
        on_delete=models.CASCADE         # order
    )
    product = models.ForeignKey(                                                   # One
        Product,
        on_delete=models.PROTECT    # product
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    class Meta:
        verbose_name_plural = "عناصر الطلب "


    def __str__(self):
        return f"{self.product.name} × {self.quantity}"