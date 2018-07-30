from django.shortcuts import render


def self_test(request):
    return render(request, 'self_test.html', {})
