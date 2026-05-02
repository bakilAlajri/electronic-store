from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image', 'category', 'brand']

# ======================
#  نموذج إنشاء حساب
# ======================
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="الاسم الأول")
    last_name = forms.CharField(max_length=50, required=True, label="الاسم الأخير")
    email = forms.EmailField(required=True, label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]


# ======================
#  نموذج تسجيل الدخول
# ======================
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")


# ======================
#  نموذج تحديث بيانات المستخدم (الملف الشخصي)
# ======================
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, label="الاسم الأول")
    last_name = forms.CharField(max_length=50, required=True, label="الاسم الأخير")
    email = forms.EmailField(required=True, label="البريد الإلكتروني")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['student_id', 'full_name', 'address', 'phone']
