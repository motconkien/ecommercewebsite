from django.shortcuts import render, HttpResponse

# Create your views here.
def user(request):
    return HttpResponse("Users page say hello")