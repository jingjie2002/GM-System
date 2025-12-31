"""
统一响应格式渲染器

功能:
将所有成功响应也封装成统一格式:
{
    "code": 200,
    "message": "success",
    "data": 实际数据
}
"""

from rest_framework.renderers import JSONRenderer


class UnifiedResponseRenderer(JSONRenderer):
    """
    统一响应格式渲染器
    
    继承自 JSONRenderer，在渲染时将数据包装成统一格式
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        重写渲染方法，统一响应格式
        
        Args:
            data: 原始响应数据
            accepted_media_type: 媒体类型
            renderer_context: 渲染上下文
            
        Returns:
            bytes: JSON 字节串
        """
        # 获取响应对象
        response = renderer_context.get('response') if renderer_context else None
        
        # 如果数据已经是统一格式（由异常处理器处理过），直接渲染
        if isinstance(data, dict) and 'code' in data and 'message' in data:
            return super().render(data, accepted_media_type, renderer_context)
        
        # 判断响应状态
        if response and response.status_code >= 400:
            # 错误响应，由异常处理器处理，理论上不会走到这里
            # 但为了健壮性，还是处理一下
            unified_data = {
                "code": response.status_code,
                "message": data.get('detail', '请求失败') if isinstance(data, dict) else str(data),
                "data": None
            }
        else:
            # 成功响应，包装成统一格式
            unified_data = {
                "code": response.status_code if response else 200,
                "message": "success",
                "data": data
            }
        
        return super().render(unified_data, accepted_media_type, renderer_context)
