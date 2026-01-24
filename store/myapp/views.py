from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction, connection
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from urllib.parse import quote_plus
from .models import Product, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt






def index(request):
    products = Product.objects.all()[:8]
    return render(request, 'myapp/index.html', {'products': products})


def products(request):
    products = Product.objects.all()
    return render(request, 'myapp/products.html', {'products': products})


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'myapp/product-detail.html', {'product': product})



def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    return redirect('cart')



def cart(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0
    updated_cart = {}

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue  # تجاهل المنتج غير الموجود

        item_total = product.price * qty
        total_price += item_total

        cart_items.append({
            "product": product,
            "quantity": qty,
            "total": item_total,
        })

        updated_cart[product_id] = qty

    request.session["cart"] = updated_cart

    return render(request, "myapp/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


def update_cart_quantity(request, product_id, qty):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    qty = int(qty)
    if qty <= 0:
        qty = 1

    cart[product_id] = qty
    request.session["cart"] = cart

    product = get_object_or_404(Product, id=product_id)
    item_total = product.price * qty

    total_price = sum(
        get_object_or_404(Product, id=int(pid)).price * q
        for pid, q in cart.items()
    )

    return JsonResponse({
        "item_total": float(item_total),
        "total_price": float(total_price)
    })



def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    return redirect('cart')


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('products')


@csrf_exempt
def checkout(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        total = product.price * quantity
        total_price += total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "total": total,
        })


    if request.method == "POST":
        full_name = request.POST.get("full_name")
        address = request.POST.get("address")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if not full_name or not address or not phone or not email:
            return render(request, "myapp/checkout.html", {
                "cart_items": cart_items,
                "total_price": total_price,
                "error": "الرجاء ملء جميع الحقول المطلوبة."
            })

        # حفظ الطلب
        # Create لجدول Order
        with transaction.atomic():
            order = Order.objects.create(
                full_name=full_name,
                address=address,
                phone=phone,
                total_price=total_price
            )

            for item in cart_items:
                # Create لجدول OrderItem
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["product"].price
                )

        # ============= 1) إرسال بريد لصاحب المتجر =============
        store_email = getattr(settings, "STORE_EMAIL", "")

        subject_admin = f"طلب جديد رقم {order.id}"
        html_admin = render_to_string("myapp/emails/admin_order.html", {
            "order": order,
            "cart_items": cart_items,
            "total_price": total_price,
            "full_name": full_name,
            "phone": phone,
            "address": address,
        })


        # ============= 2) إرسال بريد للعميل =============
        subject_user = "تأكيد طلبك"
        html_user = render_to_string("myapp/emails/user_order.html", {
            "order": order,
            "cart_items": cart_items,
            "total_price": total_price,
            "full_name": full_name,
        })

        msg_user = EmailMultiAlternatives(
            subject_user,
            "شكراً لطلبك",
            settings.EMAIL_HOST_USER,
            [email],
        )
        msg_user.attach_alternative(html_user, "text/html")
        # msg_user.send()

        # ============= 3) روابط واتساب جاهزة =============
        def clean_phone(p):
            return p.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        customer_phone = clean_phone(phone)

        customer_msg = f"مرحبًا {full_name}، تم استلام طلبك رقم {order.id} وإجمالي المبلغ {total_price} ريال."
        customer_whatsapp = f"https://wa.me/{customer_phone}?text={quote_plus(customer_msg)}"

        store_phone = clean_phone(settings.STORE_WHATSAPP_NUMBER)
        owner_msg = f"📦 طلب جديد #{order.id}\nالاسم: {full_name}\nالهاتف: {phone}\nالإجمالي: {total_price} ر.س"
        owner_whatsapp = f"https://wa.me/{store_phone}?text={quote_plus(owner_msg)}"

        request.session["last_order_whatsapp"] = customer_whatsapp
        request.session["last_order_owner_whatsapp"] = owner_whatsapp

        # تفريغ السلة
        request.session["cart"] = {}

        return redirect(reverse("order_confirmation", kwargs={"order_id": order.id}))

    return render(request, "myapp/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, "myapp/order-confirmation.html", {
        "order": order,
        "customer_phone": order.phone,
        "customer_name": order.full_name,
        "whatsapp_user": request.session.get("last_order_whatsapp"),
        "whatsapp_admin": request.session.get("last_order_owner_whatsapp"),
    })



def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # تحقق
        if not username or not password:
            return render(request, "myapp/register.html", {
                "error": "جميع الحقول مطلوبة"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "myapp/register.html", {
                "error": "اسم المستخدم موجود مسبقًا"
            })
            
            

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)  # تسجيل دخول مباشر بعد التسجيل
        return redirect("index")

    return render(request, "myapp/register.html")




def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "myapp/login.html", {
                "error": "معلومات الدخول غير صحيحة"
            })

    return render(request, "myapp/login.html")






# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

# #s
#         query = f"""
#         SELECT * FROM auth_user
#         WHERE username = '{username}'
#         AND password = '{password}'
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             user = cursor.fetchone()
# #e
#         if user:
#             return redirect("index")
#         else:
#             return render(request, "myapp/login.html", {
#                 "error": "معلومات الدخول غير صحيحة"
#             })

#    return render(request, "myapp/login.html")









def logout_view(request):
    logout(request)
    return redirect("login")


def offers(request):
    return render(request, 'myapp/offers.html')




@staff_member_required
# read of order
def orders_list(request):
    orders = Order.objects.all().order_by('-id')
    return render(request, "myapp/admin/orders_list.html", {"orders": orders})



@staff_member_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        Product.objects.create(
            name=name,
            price=price,
            image=image
        )
        return redirect("products")

    return render(request, "myapp/add_product.html")

@staff_member_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.description = request.POST.get("description")
        product.category = request.POST.get("category")
        product.brand = request.POST.get("brand")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()
        return redirect("products")

    return render(request, "myapp/edit_product.html", {"product": product})


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect("products")
    return render(request, "myapp/delete_product.html", {"product": product})