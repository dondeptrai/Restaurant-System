from django.http import HttpResponse
from django.template import loader
from .models import RestaurantTable,Order
from django.db.models import Q
from datetime import datetime
from django.shortcuts import render
from django.utils import timezone

def main(request):
    # Lấy các bảng đặt chỗ theo từng khu vực
    main_dining_tables = RestaurantTable.objects.filter(location_seat='main_dining')
    out_door = RestaurantTable.objects.filter(location_seat='outdoor')
    roof_top = RestaurantTable.objects.filter(location_seat='rooftop')

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
