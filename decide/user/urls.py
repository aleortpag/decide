from django.urls import path
from .views import AvailableVotingsView
from booth.views import BoothView


urlpatterns = [
    path('<int:user_id>/', AvailableVotingsView.as_view(), name="user"),
]
