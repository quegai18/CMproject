from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.conf import settings


class CmproMiddleware(MiddlewareMixin):
    """这个自定义中间件用于检验当前用户的权限url是否支持访问"""

    def process_request(self, request):
        if request.path not in settings.WHITE_LIST:
            if not request.user.is_active:
                return redirect(reverse("login"))