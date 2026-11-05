
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('legal/', views.legal, name='legal'),
    path('help/', views.help, name='help'),
    path('mail/', views.mail, name='mail'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('account/', views.account, name='account'),
]
