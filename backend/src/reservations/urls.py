from django.urls import path
from . import views

app_name = 'reservations'
 
urlpatterns = [
    # Las URLs de la API se añadirán más tarde
    path('get_creators/', views.get_creators, name='get_creators'),
] 