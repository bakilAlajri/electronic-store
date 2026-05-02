from django.contrib import admin
from .models import Product, Order, OrderItem, UserProfile


admin.site.register(Product)

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'id')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id','order','product','quantity','price')
    search_fields = ('order__id','product__name')



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('student_id','user','full_name','phone',)
    search_fields = ('student_id','full_name','user__username',)
