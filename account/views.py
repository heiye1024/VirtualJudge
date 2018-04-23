from django.contrib import auth
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.views import Response
from account.models import UserProfile
from account.serializers import (LoginSerializer, RegisterSerializer, ChangePasswordSerializer, RankSerializer,
                                 HookSerializer,
                                 UserProfileSerializer)
from utils.response import res_format, Message
from django.db import DatabaseError


class ChangePasswordAPI(APIView):
    def post(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                if user is not None:
                    return Response(res_format(UserProfileSerializer(user).data, status=Message.SUCCESS))
                return Response(res_format('Change password failed', status=Message.ERROR))
            return Response(res_format(serializer.errors, status=Message.ERROR))
        return Response(res_format('Login required', status=Message.ERROR))


class SessionAPI(APIView):
    def post(self, request, **kwargs):
        if request.user and request.user.is_authenticated:
            return Response(res_format(str(request.user), status=Message.SUCCESS))
        return Response(res_format('Login required', status=Message.ERROR))


class ProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        return Response(res_format('Login required', Message.ERROR))


class WebhookAPI(APIView):
    def post(self, request, **kwargs):
        pass


class LoginAPI(APIView):
    def get(self, request, **kwargs):
        return Response(res_format('Login required', Message.ERROR))

    def post(self, request, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.login(request)
            if user:
                return Response(res_format(UserProfileSerializer(user).data, Message.SUCCESS),
                                status=status.HTTP_200_OK)
            else:
                return Response(res_format('Incorrect username or password', Message.ERROR))
        return Response(res_format(serializer.errors, Message.ERROR))


class LogoutAPI(APIView):
    def delete(self, request, **kwargs):
        auth.logout(request)
        return Response(res_format('Logout success'))


class RegisterAPI(APIView):
    def post(self, request, **kwargs):
        register = RegisterSerializer(data=request.data)
        if register.is_valid():
            if register.save():
                return Response(res_format('Register success'))
            else:
                return Response(res_format('System error', status=Message.ERROR))
        return Response(res_format(register.errors, status=Message.ERROR))


class HookAPI(APIView):
    def get(self, request, **kwargs):
        if request.user is None or request.user.is_authenticated is False:
            return Response(res_format('Login required', status=Message.ERROR))
        try:
            user = UserProfile.objects.get(username=str(request.user))
            return Response(res_format(user.hook))
        except DatabaseError:
            return Response(res_format('System error', status=Message.ERROR))

    def delete(self, request, **kwargs):
        if request.user is None or request.user.is_authenticated is False:
            return Response(res_format('Login required', status=Message.ERROR))
        UserProfile.objects.filter(username=str(request.user)).update(hook=None)
        return Response(res_format('Delete hook url success'))

    def post(self, request, **kwargs):
        if request.user is None or request.user.is_authenticated is False:
            return Response(res_format('Login required', status=Message.ERROR))
        serializer = HookSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.save(str(request.user)):
                return Response(res_format('Update hook url success'))
            return Response(res_format('System error', status=Message.ERROR))
        return Response(res_format('Post data not valid', status=Message.ERROR))


class RankAPI(APIView):
    def post(self, request, **kwargs):
        try:
            users = UserProfile.objects.all().order_by('-accepted')[:20]
            return Response(res_format(RankSerializer(users, many=True).data))
        except DatabaseError:
            return Response(res_format('System error', status=Message.ERROR))
