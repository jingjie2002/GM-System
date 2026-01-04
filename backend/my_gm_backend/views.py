from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

class UserProfileView(APIView):
    """
    管理员个人中心接口
    GET: 获取个人信息
    POST: 修改密码
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取当前登录管理员信息"""
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login,
            "date_joined": user.date_joined,
        })

    def post(self, request):
        """修改密码"""
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"code": 400, "message": "请输入旧密码和新密码"}, status=400)

        if not user.check_password(old_password):
            return Response({"code": 400, "message": "旧密码错误"}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"code": 200, "message": "密码修改成功，请重新登录"})