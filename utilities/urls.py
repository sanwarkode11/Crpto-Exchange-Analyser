rom django.urls import path
from .views import VersionViewSet

urlpatterns = [
    path('version/', VersionViewSet.as_view()),
]
