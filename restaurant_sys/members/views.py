from django.http import HttpResponse
from django.template import loader
from .models import RestaurantTable, Order, OrderTable, Customer
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render, redirect
from django.utils import timezone

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
        customer = Customer.objects.get(id=1)  #cái này test nên cứ mặc định là customer id 1 
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
