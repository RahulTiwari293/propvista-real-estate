from django.contrib import admin
from .models import Realtor, Listing, Contact


@admin.register(Realtor)
class RealtorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_mvp', 'hire_date')
    list_filter = ('is_mvp',)
    search_fields = ('name', 'email')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'state', 'price', 'bedrooms', 'is_published', 'realtor', 'list_date')
    list_filter = ('is_published', 'state', 'city')
    list_editable = ('is_published',)
    search_fields = ('title', 'city', 'description')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'listing', 'email', 'phone', 'contact_date')
    search_fields = ('name', 'email')
