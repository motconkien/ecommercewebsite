from django.urls import path
from . import views

name = "app_order"
urlpatterns = [
    path('', views.order, name='order'),
]