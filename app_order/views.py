from django.shortcuts import render, HttpResponse

# Create your views here.
def order(request):
    return HttpResponse("Order pages say hello")