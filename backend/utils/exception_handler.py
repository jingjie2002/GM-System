"""
全局异常处理器

功能:
1. 拦截所有 API 异常 (404, 403, 500 等)
2. 将异常封装成统一的 JSON 格式
3. 500 错误时记录详细日志

统一响应格式:
{
    "code": 状态码,
    "message": "提示信息",
    "data": 数据内容 (错误时为 null)
}
"""

import logging
import traceback
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
    NotAuthenticated,
    ValidationError,
)
from django.http import Http404
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

# 配置日志
logger = logging.getLogger(__name__)


# 状态码对应的中文消息
ERROR_MESSAGES = {
    400: "请求参数错误",
    401: "未授权，请先登录",
    403: "没有权限执行此操作",
    404: "请求的资源不存在",
    405: "请求方法不允许",
    500: "服务器内部错误",
}


def custom_exception_handler(exc, context):
    """
    自定义全局异常处理器
    
    Args:
        exc: 异常实例
        context: 异常上下文 (包含 request, view 等信息)
        
    Returns:
        Response: 统一格式的响应
    """
    # 获取请求和视图信息
    request = context.get('request')
    view = context.get('view')
    
    # 先调用 DRF 默认的异常处理器
    response = drf_exception_handler(exc, context)
    
    # ===== 处理 DRF 能识别的异常 =====
    if response is not None:
        code = response.status_code
        
        # 提取错误消息
        if isinstance(exc, ValidationError):
            # 验证错误，提取详细信息
            message = _extract_validation_errors(response.data)
        elif isinstance(exc, NotAuthenticated):
            message = "未授权，请先登录"
        elif isinstance(exc, AuthenticationFailed):
            message = "认证失败，Token无效或已过期"
        elif isinstance(exc, PermissionDenied):
            message = "没有权限执行此操作"
        elif isinstance(exc, NotFound):
            message = "请求的资源不存在"
        else:
            # 其他异常，使用默认消息
            message = ERROR_MESSAGES.get(code, str(exc))
        
        # 封装成统一格式
        response.data = {
            "code": code,
            "message": message,
            "data": None
        }
        
        return response
    
    # ===== 处理 DRF 无法识别的异常 (500 错误) =====
    
    # 记录详细错误日志
    logger.error(
        f"[500 服务器错误]\n"
        f"请求路径: {request.path if request else 'Unknown'}\n"
        f"请求方法: {request.method if request else 'Unknown'}\n"
        f"视图: {view.__class__.__name__ if view else 'Unknown'}\n"
        f"异常类型: {type(exc).__name__}\n"
        f"异常信息: {str(exc)}\n"
        f"堆栈追踪:\n{traceback.format_exc()}"
    )
    
    # 返回统一格式的 500 响应
    from rest_framework.response import Response
    from rest_framework import status
    
    return Response(
        {
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "data": None
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _extract_validation_errors(errors):
    """
    从验证错误中提取可读的错误消息
    
    Args:
        errors: DRF 的错误字典
        
    Returns:
        str: 可读的错误消息
    """
    if isinstance(errors, dict):
        messages = []
        for field, error_list in errors.items():
            if isinstance(error_list, list):
                for error in error_list:
                    if field == 'non_field_errors':
                        messages.append(str(error))
                    else:
                        messages.append(f"{field}: {error}")
            else:
                messages.append(f"{field}: {error_list}")
        return "; ".join(messages) if messages else "请求参数错误"
    elif isinstance(errors, list):
        return "; ".join(str(e) for e in errors)
    else:
        return str(errors)
