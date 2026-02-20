from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from .models import Listing, Realtor, Contact


# ─── DRF Serializers ────────────────────────────────────────────────────────────

class ListingSerializer(serializers.ModelSerializer):
    price_inr = serializers.ReadOnlyField()
    realtor_name = serializers.CharField(source='realtor.name', default='', read_only=True)
    listing_type_display = serializers.CharField(source='get_listing_type_display', read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'address', 'city', 'state', 'price', 'price_inr',
                  'bedrooms', 'bathrooms', 'sqft', 'photo_main', 'listing_type',
                  'listing_type_display', 'is_published', 'list_date', 'realtor_name']


# ─── REST API Views ──────────────────────────────────────────────────────────────

@api_view(['GET'])
def api_listings(request):
    qs = Listing.objects.filter(is_published=True).order_by('-list_date')
    for param, field in [
        ('city', 'city__icontains'),
        ('state', 'state__iexact'),
        ('bedrooms', 'bedrooms__gte'),
        ('price', 'price__lte'),
        ('q', 'title__icontains'),
        ('type', 'listing_type__iexact'),
    ]:
        val = request.query_params.get(param)
        if val:
            qs = qs.filter(**{field: val})
    serializer = ListingSerializer(qs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def api_listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_published=True)
    serializer = ListingSerializer(listing, context={'request': request})
    return Response(serializer.data)


# ─── Page Views ─────────────────────────────────────────────────────────────────

def index(request):
    context = {
        'listings': Listing.objects.filter(is_published=True).order_by('-list_date')[:6],
        'realtors': Realtor.objects.order_by('-is_mvp', '-hire_date')[:3],
        'for_sale_count': Listing.objects.filter(is_published=True, listing_type='sale').count(),
        'for_rent_count': Listing.objects.filter(is_published=True, listing_type='rent').count(),
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html', {
        'realtors': Realtor.objects.order_by('-is_mvp', '-hire_date'),
    })


def listings(request):
    qs = Listing.objects.filter(is_published=True).order_by('-list_date')
    listing_type = request.GET.get('type')
    if listing_type in ('sale', 'rent'):
        qs = qs.filter(listing_type=listing_type)
    paginator = Paginator(qs, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'listings.html', {
        'listings': page,
        'current_type': listing_type or 'all',
    })


def listing(request, pk):
    return render(request, 'listing.html', {
        'listing': get_object_or_404(Listing, pk=pk, is_published=True),
    })


def search(request):
    qs = Listing.objects.filter(is_published=True)
    q = request.GET
    if q.get('keywords'):    qs = qs.filter(title__icontains=q['keywords'])
    if q.get('city'):        qs = qs.filter(city__icontains=q['city'])
    if q.get('state'):       qs = qs.filter(state__iexact=q['state'])
    if q.get('bedrooms'):    qs = qs.filter(bedrooms__gte=q['bedrooms'])
    if q.get('price'):       qs = qs.filter(price__lte=q['price'])
    if q.get('listing_type') in ('sale', 'rent'):
        qs = qs.filter(listing_type=q['listing_type'])
    return render(request, 'search.html', {
        'listings': qs.order_by('-list_date'),
        'values': q,
    })


def contact(request):
    if request.method != 'POST':
        return redirect('listings')
    listing_obj = get_object_or_404(Listing, pk=request.POST.get('listing_id'))
    if request.user.is_authenticated and Contact.objects.filter(listing=listing_obj, user=request.user).exists():
        messages.error(request, 'You already submitted an inquiry for this property.')
        return redirect('listing', pk=listing_obj.pk)
    Contact.objects.create(
        listing=listing_obj,
        user=request.user if request.user.is_authenticated else None,
        name=request.POST.get('name'),
        email=request.POST.get('email'),
        phone=request.POST.get('phone', ''),
        message=request.POST.get('message', ''),
    )
    messages.success(request, 'Your inquiry has been sent! A realtor will contact you soon.')
    return redirect('listing', pk=listing_obj.pk)


# ─── Auth Views ──────────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        p = request.POST
        if p['password'] != p['password2']:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=p['username']).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=p['email']).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=p['username'], password=p['password'],
                email=p['email'], first_name=p['first_name'], last_name=p['last_name'])
            auth.login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Account created.')
            return redirect('dashboard')
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            auth.login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    auth.logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('index')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'dashboard.html', {
        'contacts': Contact.objects.filter(user=request.user).order_by('-contact_date'),
        'my_listings': Listing.objects.filter(posted_by=request.user).order_by('-list_date'),
    })


# ─── Property Posting ────────────────────────────────────────────────────────────

@login_required(login_url='/login/')
def post_listing(request):
    if request.method == 'POST':
        p = request.POST
        f = request.FILES
        listing = Listing(
            posted_by=request.user,
            listing_type=p.get('listing_type', 'sale'),
            title=p.get('title', ''),
            address=p.get('address', ''),
            city=p.get('city', ''),
            state=p.get('state', ''),
            price=int(p.get('price', 0)),
            bedrooms=int(p.get('bedrooms', 1)),
            bathrooms=float(p.get('bathrooms', 1.0)),
            sqft=int(p.get('sqft', 0)),
            description=p.get('description', ''),
            is_published=False,  # needs admin approval
        )
        if f.get('photo_main'):
            listing.photo_main = f['photo_main']
        if f.get('photo_1'):
            listing.photo_1 = f['photo_1']
        if f.get('photo_2'):
            listing.photo_2 = f['photo_2']
        listing.save()
        messages.success(request, '🎉 Your listing has been submitted! It will go live after admin review.')
        return redirect('dashboard')
    return render(request, 'post_listing.html')
