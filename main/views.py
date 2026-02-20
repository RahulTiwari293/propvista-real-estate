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
    if q.get('keywords'):  qs = qs.filter(title__icontains=q['keywords'])
    if q.get('city'):      qs = qs.filter(city__icontains=q['city'])
    if q.get('state'):     qs = qs.filter(state__iexact=q['state'])
    if q.get('bedrooms'):  qs = qs.filter(bedrooms__gte=q['bedrooms'])
    if q.get('price'):     qs = qs.filter(price__lte=q['price'])
    if q.get('listing_type') in ('sale', 'rent'):
        qs = qs.filter(listing_type=q['listing_type'])
    if q.get('property_type') in ('apartment', 'house', 'villa', 'land', 'commercial'):
        qs = qs.filter(property_type=q['property_type'])
    state = q.get('state', '')
    ptype = q.get('property_type', '')
    ltype = q.get('listing_type', '')
    price_v = q.get('price', '')
    states = ['Maharashtra', 'Karnataka', 'Delhi', 'Tamil Nadu', 'Gujarat',
              'Telangana', 'Kerala', 'Rajasthan', 'West Bengal',
              'Uttar Pradesh', 'Punjab', 'Haryana']
    # Pre-compute selected booleans so templates need no == comparisons
    return render(request, 'search.html', {
        'listings':           qs.order_by('-list_date'),
        'values':             q,
        'state_opts':         [{'name': s, 'sel': state == s} for s in states],
        'ptype_apartment':    ptype == 'apartment',
        'ptype_house':        ptype == 'house',
        'ptype_villa':        ptype == 'villa',
        'ptype_land':         ptype == 'land',
        'ptype_commercial':   ptype == 'commercial',
        'ltype_sale':         ltype == 'sale',
        'ltype_rent':         ltype == 'rent',
        'price_20l':          price_v == '2000000',
        'price_50l':          price_v == '5000000',
        'price_1cr':          price_v == '10000000',
        'price_2cr':          price_v == '20000000',
        'price_5cr':          price_v == '50000000',
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
    u = request.user
    my_listings = Listing.objects.filter(posted_by=u).order_by('-list_date')
    return render(request, 'dashboard.html', {
        'contacts': Contact.objects.filter(user=u).order_by('-contact_date'),
        'my_listings': my_listings,
        'live_count': my_listings.filter(is_published=True).count(),
        'display_name': u.first_name or u.username,
    })



# ─── Property Posting ────────────────────────────────────────────────────────────

def _safe_int(val, default=None):
    """Return int(val) or default if val is empty / non-numeric."""
    try:
        return int(val) if val and str(val).strip() else default
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=None):
    """Return float(val) or default if val is empty / non-numeric."""
    try:
        return float(val) if val and str(val).strip() else default
    except (ValueError, TypeError):
        return default


@login_required(login_url='/login/')
def post_listing(request):
    if request.method == 'POST':
        p = request.POST
        f = request.FILES
        try:
            listing = Listing(
                posted_by=request.user,
                listing_type=p.get('listing_type', 'sale'),
                property_type=p.get('property_type', 'apartment'),
                title=p.get('title', '').strip(),
                address=p.get('address', '').strip(),
                city=p.get('city', '').strip(),
                state=p.get('state', '').strip(),
                price=_safe_int(p.get('price'), 0),
                bedrooms=_safe_int(p.get('bedrooms')),          # nullable — None for land
                bathrooms=_safe_float(p.get('bathrooms')),      # nullable — None for land
                sqft=_safe_int(p.get('sqft')),                  # nullable
                description=p.get('description', '').strip(),
                is_published=True,   # goes live immediately
            )
            if f.get('photo_main'):
                listing.photo_main = f['photo_main']
            if f.get('photo_1'):
                listing.photo_1 = f['photo_1']
            if f.get('photo_2'):
                listing.photo_2 = f['photo_2']
            listing.save()
            messages.success(request, '🎉 Listing submitted! It will go live after admin review.')
            return redirect('dashboard')
        except Exception as exc:
            messages.error(request, f'Could not submit listing: {exc}')
    return render(request, 'post_listing.html')
