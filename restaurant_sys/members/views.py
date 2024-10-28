from django.http import HttpResponse
from django.template import loader
from .models import RestaurantTable, Order, OrderTable, Customer
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Customer
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django import forms
from django.contrib.auth import logout

def main(request):
    order_tables = OrderTable.objects.all()
    main_dining_tables = RestaurantTable.objects.filter(location_seat='main_dining')
    out_door = RestaurantTable.objects.filter(location_seat='outdoor')
    roof_top = RestaurantTable.objects.filter(location_seat='rooftop')

    #Xử lý cập nhật thời gian trạng thái bàn
    for order_table in order_tables:
        order_table.check_and_update_table_status()
    
        
    # Xác định khoảng thời gian cho bữa trưa và bữa tối
    lunch_start_time = timezone.datetime.strptime('6:00 AM', '%I:%M %p').time()
    lunch_end_time = timezone.datetime.strptime('2:00 PM', '%I:%M %p').time()

    dinner_start_time = timezone.datetime.strptime('5:00 PM', '%I:%M %p').time()
    dinner_end_time = timezone.datetime.strptime('10:00 PM', '%I:%M %p').time()

    # Lấy các đơn đặt chỗ cho bữa trưa
    lunch_orders = Order.objects.filter(
        begin_time__time__gte=lunch_start_time,
        begin_time__time__lt=lunch_end_time
    ).prefetch_related('ordertable_set')

    # Lấy các đơn đặt chỗ cho bữa tối
    dinner_orders = Order.objects.filter(
        begin_time__time__gte=dinner_start_time,
        begin_time__time__lt=dinner_end_time
    ).prefetch_related('ordertable_set')

    context = {
        'main_dining_tables': main_dining_tables,
        'out_door': out_door,
        'roof_top': roof_top,
        'lunch_orders': lunch_orders,
        'dinner_orders': dinner_orders,
    }

    # Trả về template với context
    return render(request, 'home.html', context)

def testing(request):
  tables = RestaurantTable.objects.all()
  template = loader.get_template('testing.html')
  context = {
    'tables': tables,
  }
  return HttpResponse(template.render(context, request))


#tìm kiếm
def search_orders(request):
    search_query = request.GET.get('search', '')
    date_query = request.GET.get('date', '')
    status_query = request.GET.get('status', '').lower()
    time_query = request.GET.get('time', '')

    # Tạo một truy vấn ban đầu
    orders = Order.objects.all()

    # Tìm kiếm theo số lượng người
    if search_query:
        try:
            num_customers = int(search_query)
            orders = orders.filter(numof_customer=num_customers)
        except ValueError:
            orders = orders.filter(
                Q(customer__customer_name__icontains=search_query) |
                Q(begin_time__icontains=search_query) |
                Q(end_time__icontains=search_query)
            )

    # Tìm kiếm theo ngày đặt bàn
    if date_query:
        try:
            reservation_date = datetime.strptime(date_query, '%d/%m/%Y').date()
            orders = orders.filter(begin_time__date=reservation_date)
        except ValueError:
            try:
                reservation_date = datetime.strptime(date_query, '%Y-%m-%d').date()
                orders = orders.filter(begin_time__date=reservation_date)
            except ValueError:
                pass

        # Tìm kiếm theo trạng thái bàn
    if status_query in ['available', 'reserved']:
        # Lọc theo trạng thái bàn
        orders = orders.filter(
            ordertable__table__status=status_query
        ).distinct()  # Sử dụng distinct để tránh trùng lặp đơn hàng

    # Tìm kiếm theo thời gian đặt bàn
    if time_query:
        try:
            reservation_time = datetime.strptime(time_query, '%H:%M').time()
            orders = orders.filter(
                Q(ordertable__begin_time__time=reservation_time) |
                Q(ordertable__end_time__time=reservation_time)
            )
        except ValueError:
            pass

    template = loader.get_template('search_results.html')
    context = {
        'orders': orders,
    }
    return HttpResponse(template.render(context, request))

def add_order(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')  
        if customer_id:
            customer = Customer.objects.get(id=customer_id)  # Lấy khách hàng dựa trên ID từ phiên
            numof_customer = request.POST.get('numof_customer')
            begin_time = request.POST.get('begin_time')
            end_time = request.POST.get('end_time')
            table_id = request.POST.get('table_id')

        if not table_id:
            return HttpResponse("Table ID is missing", status=400)
        
        table = RestaurantTable.objects.get(id=table_id)
        order = Order.objects.create(
            customer=customer,
            numof_customer=numof_customer,
            begin_time=begin_time,
            end_time=end_time,
        )
        OrderTable.objects.create(
            order=order,
            table=table,
            begin_time=begin_time,
            end_time=end_time
        )
        table.status = 'reserved'
        table.save()

        return redirect('main')
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
            return redirect('login')
    else:
        form = Users()

    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        password = request.POST.get('password')
        
        if customer_name and password:
            try:
              
                customers = Customer.objects.filter(customer_name=customer_name)

                if customers.exists():
                    customer = customers.first()  # Lấy khách hàng đầu tiên trong danh sách

                    # Kiểm tra mật khẩu
                    if check_password(password, customer.password):
                        
                        request.session['customer_id'] = customer.id
                        request.session['customer_name'] = customer.customer_name
                        return redirect('main')
                    else:
                        # Mật khẩu sai
                        messages.error(request, "Sai mật khẩu. Vui lòng thử lại.")
                else:
                    # Không tìm thấy khách hàng
                    messages.error(request, "Tên khách hàng không tồn tại. Vui lòng thử lại.")
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {str(e)}")
        else:
            messages.error(request, "Vui lòng điền tên khách hàng và mật khẩu.")

    return render(request, 'login.html')

def logout_view(request):
    # Xóa thông tin khách hàng khỏi session
    logout(request)
    # Chuyển hướng về trang chính hoặc trang đăng nhập
    return redirect('main')
