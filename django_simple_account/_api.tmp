from django.contrib.auth.models import User
from django.db import transaction

try:
    from rest_framework import generics, response, serializers, permissions, pagination, status
    from rest_framework.generics import get_object_or_404
except ImportError:
    print('There was no such module installed')

from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(use_url=True, read_only=True, allow_null=True)

    class Meta:
        model = models.Profile
        fields = ('gender', 'birth_date', 'phone', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    detail = serializers.HyperlinkedIdentityField(
        view_name='accounts-api-user-detail',
        lookup_field="id",
        read_only=True,
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'date_joined', 'is_staff', 'is_active', 'is_superuser',
                  'profile', 'detail'
                  )

    def create(self, validated_data):
        profile = validated_data.pop('profile')
        with transaction.atomic():
            instance = User.objects.create_user(**validated_data)

            data = dict(profile)
            models.Profile.objects.filter(user=instance).update(**data)
            instance.refresh_from_db()
            return instance

    def update(self, instance, validated_data):
        profile = validated_data.pop('profile')
        with transaction.atomic():
            User.objects.filter(id=instance.id).update(**validated_data)

            data = dict(profile)
            models.Profile.objects.filter(user=instance).update(**data)
            instance.refresh_from_db()
            return instance


class APIUser(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        return User.objects.all().order_by('-id')


class APIUserDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        return User.objects.all().order_by('-id')

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.kwargs.get('id'))
