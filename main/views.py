from django.shortcuts import render

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