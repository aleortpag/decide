from django.urls import path
from .views import AvailableVotingsView


urlpatterns = [
    path('<int:user_id>/', AvailableVotingsView.as_view(), name="user"),
]
