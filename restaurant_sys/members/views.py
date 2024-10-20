from django.http import HttpResponse
from django.template import loader
from .models import RestaurantTable


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
  templete = loader.get_template('testing.html')
  context = {
    'tables': tables,
  }
  return HttpResponse(templete.render(context, request))


