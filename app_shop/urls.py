from django.urls import path
from . import views

name = 'app_shop'
urlpatterns = [
    path('', views.home, name='home'),
]