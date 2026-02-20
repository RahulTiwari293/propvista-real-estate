from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('listings/', views.listings, name='listings'),
    path('listings/<int:pk>/', views.listing, name='listing'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),
    path('post-listing/', views.post_listing, name='post-listing'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # REST API
    path('api/listings/', views.api_listings, name='api-listings'),
    path('api/listings/<int:pk>/', views.api_listing_detail, name='api-listing-detail'),
]
