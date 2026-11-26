import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.validators import validate_image_file_extension
from .models import Item

# HTML Template Page Views

def index(request):
    return render(request, 'main/index.html')

def legal(request):
    return render(request, 'main/legal.html')

def help(request):
    return render(request, 'main/help.html')

def mail(request):
    return render(request, 'main/mail.html')

def search(request):
    return render(request, 'main/search.html')

def wishlist(request):
    return render(request, 'main/wishlist.html')

def account(request):
    from .forms import EmailAuthenticationForm
    listings = Item.objects.filter(owner=request.user, is_available=True) if request.user.is_authenticated else Item.objects.none()
    return render(request, 'main/account.html', {'profile': getattr(request.user, 'profile', None) if request.user.is_authenticated else None, 'listings': listings, 'form': EmailAuthenticationForm(request), 'next': request.GET.get('next', '')})


@login_required
def create_post(request):
    from .forms import ItemForm
    form = ItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.owner = request.user
        item.save()
        messages.success(request, 'Your listing has been published.')
        return redirect('account')
    return render(request, 'main/create_post.html', {'form': form})


@require_POST
def register(request):
    """Register a new SDU student account."""
    from django.contrib.auth import get_user_model
    from django.contrib.auth.hashers import check_password
    import re
    
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')
    
    User = get_user_model()
    
    # Validation
    if not name or not email or not password:
        messages.error(request, 'All fields are required.')
        return redirect('account')
    
    if password != password2:
        messages.error(request, 'Passwords do not match.')
        return redirect('account')
    
    if len(password) < 8:
        messages.error(request, 'Password must be at least 8 characters.')
        return redirect('account')
    
    # Check if email is SDU email
    if not email.endswith('@sdu.edu.kz') and not email.endswith('@stu.sdu.edu.kz'):
        messages.error(request, 'Please use your SDU email address.')
        return redirect('account')
    
    if User.objects.filter(email__iexact=email).exists():
        messages.error(request, 'An account with this email already exists.')
        return redirect('account')
    
    # Create user
    parts = name.split(None, 1)
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts) > 1 else ''
    
    user = User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    from django.contrib.auth import login
    login(request, user, backend='main.authentication.EmailBackend')
    
    messages.success(request, 'Account created successfully!')
    return redirect('index')



def api_items(request):
    if request.method == 'GET':
        query = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        listing_type = request.GET.get('type', '').strip()

        items = Item.objects.filter(is_available=True)

        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(contact__icontains=query)
            )

        if category:
            items = items.filter(category=category)
        if listing_type in dict(Item.TYPE_CHOICES):
            items = items.filter(listing_type=listing_type)

        data = [item.to_dict() for item in items]
        return JsonResponse({'success': True, 'count': len(data), 'items': data}, status=200)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)
        try:
            # Support both JSON payload and regular form encoded data
            if request.content_type == 'application/json':
                body = json.loads(request.body.decode('utf-8'))
            else:
                body = request.POST

            title = body.get('title', '').strip()
            description = body.get('description', '').strip()
            category = body.get('category', 'other').strip()
            contact = body.get('contact', '').strip()
            listing_type = body.get('type', 'Sale').strip()
            price = body.get('price') or None
            image = request.FILES.get('image')
            if image:
                if image.size > 5 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': 'Image must be 5 MB or smaller.'}, status=400)
                validate_image_file_extension(image)
                get_image_dimensions(image)

            if not title:
                return JsonResponse({'success': False, 'error': 'Field "title" is required.'}, status=400)

            if not contact:
                return JsonResponse({'success': False, 'error': 'Field "contact" is required.'}, status=400)

            if listing_type not in dict(Item.TYPE_CHOICES):
                return JsonResponse({'success': False, 'error': 'Invalid listing type.'}, status=400)
            if category not in dict(Item.CATEGORY_CHOICES):
                return JsonResponse({'success': False, 'error': 'Invalid category.'}, status=400)
            # Validate category against model choices

            item = Item.objects.create(
                title=title,
                description=description,
                category=category,
                contact=contact,
                owner=request.user,
                listing_type=listing_type,
                price=price,
                image=image,
                is_available=True
            )

            return JsonResponse({'success': True, 'item': item.to_dict()}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating item: {e}", exc_info=True)
            return JsonResponse({'success': False, 'error': 'Internal server error. Please try again.'}, status=500)

    else:
        return JsonResponse(
            {'success': False, 'error': f'Method {request.method} not allowed.'},
            status=405
        )


def api_item_detail(request, item_id):
    """
    HTTP API endpoint for a single UniSwap Item.
    - GET    /api/items/<id>/ : Retrieve single item details
    - DELETE /api/items/<id>/ : Mark item as unavailable
    """
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'item': item.to_dict()}, status=200)

    elif request.method in ('PUT', 'PATCH'):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)
        if item.owner_id != request.user.id:
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
        try:
            body = json.loads(request.body.decode('utf-8'))
            for key in ('title', 'description', 'contact'):
                if key in body:
                    setattr(item, key, str(body[key]).strip())
            if 'category' in body and body['category'] in dict(Item.CATEGORY_CHOICES): item.category = body['category']
            if 'type' in body and body['type'] in dict(Item.TYPE_CHOICES): item.listing_type = body['type']
            if 'price' in body: item.price = body['price'] or None
            item.save()
            return JsonResponse({'success': True, 'item': item.to_dict()})
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid item data.'}, status=400)

    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        if item.owner_id != request.user.id and role not in ('moderator', 'admin'):
            return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)
        item.is_available = False
        item.save()
        return JsonResponse({'success': True, 'message': 'Item marked as swapped/unavailable.'}, status=200)

    else:
        return JsonResponse(
            {'success': False, 'error': f'Method {request.method} not allowed.'},
            status=405
        )


class UniSwapLoginView(LoginView):
    template_name = 'main/account.html'
    authentication_form = __import__('main.forms', fromlist=['EmailAuthenticationForm']).EmailAuthenticationForm


@require_POST
def logout_view(request):
    logout(request)
    return redirect('account')
