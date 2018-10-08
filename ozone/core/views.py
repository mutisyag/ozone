from django.shortcuts import render

# Create your views here.
def spabundle(request):
    return render(request, 'bundle.html')