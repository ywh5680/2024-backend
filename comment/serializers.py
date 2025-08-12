from rest_framework import serializers
from . import models


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    
    class Meta:
        model = models.Comment
        fields = ['id', 'content', 'parent', 'datetime', 'qq', 'email']
        extra_kwargs = {
            'parent': {'write_only': True},
            'datetime': {'read_only': True},
        }

    def validate_content(self, data):
        """验证评论内容"""
        if not data or len(data.strip()) < 1:
            raise serializers.ValidationError("评论内容不能为空")
        if len(data) > 1000:
            raise serializers.ValidationError("评论内容不能超过1000个字符")
        return data
    
    def validate_email(self, data):
        """验证邮箱格式"""
        if data and '@' not in data:
            raise serializers.ValidationError("邮箱格式不正确")
        return data
    
    def validate(self, attrs):
        """验证整体数据"""
        qq = attrs.get('qq')
        email = attrs.get('email')
        
        if qq is None and email is None:
            raise serializers.ValidationError("QQ号和邮箱至少需要提供一个")
            
        return attrs
