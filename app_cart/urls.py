from django.urls import path
from . import views

name = "app_cart"
urlpatterns = [
    path('', views.cart, name='cart'),
]