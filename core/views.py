### views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Message
from .serializers import MessageSerializer, UserSerializer
from .utils import deliver_due_messages_for_user  

@api_view(['GET'])
def root(request):
    return Response({"message": "API is live"})

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=201)
    return Response(serializer.errors, status=400)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key})

class MessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        return Response({"detail": "Use inbox or outbox endpoints."})

    @action(detail=False, methods=['get'])
    def inbox(self, request):
        deliver_due_messages_for_user(request.user)  # Auto-deliver on access
        messages = Message.objects.filter(recipient=request.user, delivered=True).order_by('-scheduled_time')
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=False, methods=['get'])
    def outbox(self, request):
        messages = Message.objects.filter(sender=request.user).order_by('-scheduled_time')
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=False, methods=['post'])
    def send(self, request):
        data = request.data.copy()
        data['sender'] = request.user.id
        serializer = MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

