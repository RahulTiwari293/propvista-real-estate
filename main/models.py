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
    # ── Listing purpose ─────────────────────────────────────
    SALE = 'sale'
    RENT = 'rent'
    LISTING_TYPE_CHOICES = [
        (SALE, 'For Sale'),
        (RENT, 'For Rent'),
    ]

    # ── Property category ───────────────────────────────────
    APARTMENT = 'apartment'
    HOUSE = 'house'
    VILLA = 'villa'
    LAND = 'land'
    COMMERCIAL = 'commercial'
    PROPERTY_TYPE_CHOICES = [
        (APARTMENT, 'Apartment / Flat'),
        (HOUSE, 'House / Bungalow'),
        (VILLA, 'Villa'),
        (LAND, 'Land / Plot'),
        (COMMERCIAL, 'Commercial'),
    ]

    realtor = models.ForeignKey(Realtor, on_delete=models.SET_NULL, null=True, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='listings')

    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default=SALE)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default=APARTMENT)

    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    price = models.IntegerField()

    # Optional for land/commercial (no bedrooms/bathrooms)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    sqft = models.IntegerField(null=True, blank=True, help_text='Area in sqft or sq.yards for land')

    description = models.TextField(blank=True)
    photo_main = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    photo_1 = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    photo_2 = models.ImageField(upload_to='listings/%Y/%m/', blank=True)
    is_published = models.BooleanField(default=False)
    list_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def price_inr(self):
        return '₹{:,}'.format(self.price)

    @property
    def type_label(self):
        return 'For Rent' if self.listing_type == self.RENT else 'For Sale'

    def get_property_type_icon(self):
        icons = {
            'apartment': 'fas fa-building',
            'house': 'fas fa-home',
            'villa': 'fas fa-landmark',
            'land': 'fas fa-mountain',
            'commercial': 'fas fa-store',
        }
        return icons.get(self.property_type, 'fas fa-home')


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
