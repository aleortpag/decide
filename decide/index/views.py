from django.shortcuts import render
from rest_framework.views import APIView


class IndexView(APIView):
    def get(self, request):
        return render(request, 'index/index.html')
