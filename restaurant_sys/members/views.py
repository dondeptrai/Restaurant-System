from django.http import HttpResponse
from django.template import loader
from .models import RestaurantTable
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect  
from django import forms
from .models import Customer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

def main(request):
   main_dining_tables = RestaurantTable.objects.filter(location_seat='main_dining')
   out_door =  RestaurantTable.objects.filter(location_seat='outdoor')
   roof_top = RestaurantTable.objects.filter(location_seat='rooftop')
   
   context = {
    'main_dining_tables': main_dining_tables,
    'out_door': out_door,
    'roof_top': roof_top,
   }
   template = loader.get_template('home.html')
   return HttpResponse(template.render(context, request))

def testing(request):
  tables = RestaurantTable.objects.all()
  template = loader.get_template('testing.html')
  context = {
    'tables': tables,
  }
  return HttpResponse(template.render(context, request))

class Users(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'email', 'phone', 'password']
def register(request):
    if request.method == 'POST':
        form = Users(request.POST)
        if form.is_valid():
            # Lưu khách hàng mới
            customer = form.save(commit=False)
            customer.password = make_password(form.cleaned_data['password'])  # Mã hóa mật khẩu
            customer.save()

            messages.success(request, "Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.")
            return redirect('main')
    else:
        form = Users()

    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        password = request.POST.get('password')
        
        if customer_name and password:  # Kiểm tra xem có giá trị không
            try:
                # Tìm khách hàng dựa trên tên
                customer = Customer.objects.get(customer_name=customer_name)

                # Kiểm tra mật khẩu
                if check_password(password, customer.password):
                    # Mật khẩu đúng, chuyển hướng về trang chính
                    messages.success(request, "Đăng nhập thành công!")
                    return redirect('main')
                else:
                    # Mật khẩu sai
                    messages.error(request, "Sai mật khẩu. Vui lòng thử lại.")
            except Customer.DoesNotExist:
                # Khách hàng không tồn tại
                messages.error(request, "Tên khách hàng không tồn tại. Vui lòng thử lại.")
        else:
            messages.error(request, "Vui lòng điền tên khách hàng và mật khẩu.")

    return render(request, 'login.html')  # Hiển thị form đăng nhập
