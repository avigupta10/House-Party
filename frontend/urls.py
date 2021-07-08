from django.urls import path
from frontend import views

app_name = 'frontend'

urlpatterns = [
    path('', views.index, name='index'),
    path('join', views.index, name='join'),
    path('create', views.index, name='create'),
    path('room/<str:code>', views.index, name='room'),
]
