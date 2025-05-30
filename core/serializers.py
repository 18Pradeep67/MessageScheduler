### serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message
from datetime import timezone 
from django.utils import timezone as dj_timezone  

from pytz import timezone as pytz_timezone


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = '__all__'
#         read_only_fields = ['created_at', 'delivered', 'delivered_at', 'sender']

#     def create(self, validated_data):
#         # sender comes from context, not from input data
#         user = self.context['request'].user
#         return Message.objects.create(sender=user, **validated_data)

class MessageSerializer(serializers.ModelSerializer):
    scheduled_time = serializers.DateTimeField()
    created_at = serializers.SerializerMethodField()
    delivered_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['created_at', 'delivered', 'delivered_at', 'sender']

    def get_created_at(self, obj):
        return self._to_ist(obj.created_at)

    def get_delivered_at(self, obj):
        return self._to_ist(obj.delivered_at)

    def _to_ist(self, dt):
        if dt is None:
            return None
        ist = pytz_timezone('Asia/Kolkata')
        return dt.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        user = self.context['request'].user
        ist = pytz_timezone('Asia/Kolkata')
        scheduled_time = validated_data.get('scheduled_time')

        if scheduled_time:
            if dj_timezone.is_naive(scheduled_time):
                scheduled_time = ist.localize(scheduled_time)
            scheduled_time = scheduled_time.astimezone(timezone.utc) 
            validated_data['scheduled_time'] = scheduled_time


        return Message.objects.create(sender=user, **validated_data)
