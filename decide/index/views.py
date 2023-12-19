from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView


class IndexView(APIView):
    def get(self, request):
        return render(request, 'index/index.html')
