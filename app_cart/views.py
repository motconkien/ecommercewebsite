from django.shortcuts import render, HttpResponse

# Create your views here.
def cart(request):
    return HttpResponse("App cart say hello")