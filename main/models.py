from django.db import models
from django.contrib.auth.models import User


class Realtor(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='realtors/', blank=True)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_mvp = models.BooleanField(default=False)
    hire_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Listing(models.Model):
    realtor = models.ForeignKey(Realtor, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    sqft = models.IntegerField()
    description = models.TextField(blank=True)
    photo_main = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    photo_1 = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    photo_2 = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    is_published = models.BooleanField(default=True)
    list_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def price_inr(self):
        return '₹{:,}'.format(self.price)


class Contact(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    contact_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} → {self.listing.title}'

    class Meta:
        unique_together = ('listing', 'user')
