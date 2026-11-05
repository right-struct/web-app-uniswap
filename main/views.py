import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
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
    return render(request, 'main/account.html')


# HTTP-based REST API for Swap Items

@csrf_exempt
def api_items(request):
    """
    HTTP API endpoint for UniSwap Item resources.
    - GET  /api/items/ : List all available swap items (supports ?search= and ?category=)
    - POST /api/items/ : Create a new swap item (accepts JSON payload)
    """
    if request.method == 'GET':
        query = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()

        items = Item.objects.filter(is_available=True)

        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(contact__icontains=query)
            )

        if category:
            items = items.filter(category=category)

        data = [item.to_dict() for item in items]
        return JsonResponse({'success': True, 'count': len(data), 'items': data}, status=200)

    elif request.method == 'POST':
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

            if not title:
                return JsonResponse({'success': False, 'error': 'Field "title" is required.'}, status=400)

            if not contact:
                return JsonResponse({'success': False, 'error': 'Field "contact" is required.'}, status=400)

            # Validate category against model choices
            valid_categories = [c[0] for c in Item.CATEGORY_CHOICES]
            if category not in valid_categories:
                category = 'other'

            item = Item.objects.create(
                title=title,
                description=description,
                category=category,
                contact=contact,
                is_available=True
            )

            return JsonResponse({'success': True, 'item': item.to_dict()}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    else:
        return JsonResponse(
            {'success': False, 'error': f'Method {request.method} not allowed.'},
            status=405
        )


@csrf_exempt
def api_item_detail(request, item_id):
    """
    HTTP API endpoint for a single UniSwap Item.
    - GET    /api/items/<id>/ : Retrieve single item details
    - DELETE /api/items/<id>/ : Mark item as unavailable
    """
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'item': item.to_dict()}, status=200)

    elif request.method == 'DELETE':
        item.is_available = False
        item.save()
        return JsonResponse({'success': True, 'message': 'Item marked as swapped/unavailable.'}, status=200)

    else:
        return JsonResponse(
            {'success': False, 'error': f'Method {request.method} not allowed.'},
            status=405
        )