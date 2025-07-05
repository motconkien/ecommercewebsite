from django.urls import path
from . import views

name = "app_user"
urlpatterns = [
    path('', views.user, name='user'),
]