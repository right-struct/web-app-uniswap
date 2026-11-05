from django.urls import path
from . import views

urlpatterns = [
    # Frontend Pages
    path('', views.index, name='index'),
    path('legal/', views.legal, name='legal'),
    path('help/', views.help, name='help'),
    path('mail/', views.mail, name='mail'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('account/', views.account, name='account'),

    # HTTP REST API Endpoints
    path('api/items/', views.api_items, name='api_items'),
    path('api/items/<int:item_id>/', views.api_item_detail, name='api_item_detail'),
]
