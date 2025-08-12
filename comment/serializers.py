from rest_framework import serializers
from . import models


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    orid = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Comment
        fields = ['id', 'content', 'datetime', 'qq', 'email', 'orid']
        extra_kwargs = {
            'datetime': {'read_only': True},
        }
    
    def get_orid(self, obj):
        """获取父评论ID"""
        return obj.parent.id if obj.parent else None
    
    def to_representation(self, instance):
        """处理数据表示，实现隐私保护"""
        representation = super().to_representation(instance)
        
        # 隐藏部分QQ号
        if representation.get('qq'):
            qq = str(representation['qq'])
            if len(qq) > 6:
                representation['qq'] = qq[:3] + "****" + qq[-2:]
            else:
                representation['qq'] = qq[:1] + "****" + qq[-1:] if len(qq) > 2 else "****"
        
        # 隐藏部分邮箱
        if representation.get('email'):
            email = representation['email']
            username, domain = email.split('@') if '@' in email else (email, '')
            if len(username) > 1:
                masked_username = username[0] + "***"
                representation['email'] = masked_username + '@' + domain if domain else masked_username
            else:
                representation['email'] = "u***@" + domain if domain else "u***"
        
        return representation
    
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
    
    def create(self, validated_data):
        """创建评论时处理orid字段"""
        # 从请求数据中获取orid
        orid = self.context['request'].data.get('orid')
        
        if orid:
            try:
                # 查找父评论
                parent = models.Comment.objects.get(id=orid)
                # 设置parent字段
                validated_data['parent'] = parent
            except models.Comment.DoesNotExist:
                raise serializers.ValidationError({"orid": f"ID为{orid}的评论不存在"})
        
        # 创建评论
        return super().create(validated_data)
