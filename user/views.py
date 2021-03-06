from django.contrib import auth
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.views import Response
from user.models import UserProfile
from user.serializers import (LoginSerializer, RegisterSerializer, ChangePasswordSerializer, RankSerializer,
                              HookSerializer,
                              UserProfileSerializer)
from utils.response import res_format, Message
from django.db import DatabaseError
import hashlib


class ChangePasswordAPI(APIView):
    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            try:
                user = UserProfile.objects.get(username=request.user)
                return Response(res_format(UserProfileSerializer(user).data, status=Message.SUCCESS))
            except:
                return Response(res_format('System Error', Message.ERROR))
        return Response(res_format('Login required', Message.ERROR))

    # 修改密码
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


class ProfileAPI(APIView):
    # 获取个人信息
    def get(self, request, **kwargs):
        if request.user and request.user.is_authenticated:
            user_profile = UserProfile.objects.get(username=request.user)
            serializer = UserProfileSerializer(user_profile)
            res_data = serializer.data
            res_data['email'] = hashlib.md5(str(res_data['email']).encode('utf-8')).hexdigest()
            return Response(res_format(res_data, status=Message.SUCCESS))
        return Response(res_format('not login', status=Message.ERROR))


class PrivilegeAPI(APIView):
    def get(self, request, **kwargs):
        if request.user and request.user.is_authenticated and request.user.is_admin:
            return Response(res_format(True, status=Message.SUCCESS))
        return Response(res_format(False, status=Message.SUCCESS))


class AuthAPI(APIView):
    # 检查登录状态
    def get(self, request, **kwargs):
        if request.user and request.user.is_authenticated:
            return Response(res_format(str(request.user), status=Message.SUCCESS))
        return Response(res_format('Login required', status=Message.ERROR))

    # 提交登录
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

    # 退出登录
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
    # 获取 hook url
    def get(self, request, **kwargs):
        if request.user is None or request.user.is_authenticated is False:
            return Response(res_format('Login required', status=Message.ERROR))
        try:
            serializer = HookSerializer(UserProfile.objects.get(username=request.user))
            return Response(res_format(serializer.data))
        except DatabaseError:
            return Response(res_format('System error', status=Message.ERROR))

    # 修改 hook url
    def post(self, request, **kwargs):
        if request.user is None or request.user.is_authenticated is False:
            return Response(res_format('Login required', status=Message.ERROR))
        serializer = HookSerializer(data=request.data)
        if serializer.is_valid():
            try:
                url = serializer.validated_data['hook']
                UserProfile.objects.filter(username=request.user).update(hook=url)
                return Response(res_format('success'))
            except:
                pass
            return Response(res_format('System error', status=Message.ERROR))
        return Response(res_format('Post data not valid', status=Message.ERROR))


class RankAPI(APIView):
    # 获取排行榜
    def get(self, request, **kwargs):
        try:
            users = UserProfile.objects.all().order_by('-accepted')[:500]
            return Response(res_format(RankSerializer(users, many=True).data))
        except DatabaseError:
            return Response(res_format('System error', status=Message.ERROR))
