### core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, signup, CustomAuthToken, root

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', root),
    path('', include(router.urls)),
    path('signup/', signup),
    path('login/', CustomAuthToken.as_view()),
]
