import re
from rest_framework import serializers
from . import models


class QQField(serializers.CharField):
    """QQ号字段，包含验证和脱敏功能"""
    default_error_messages = {
        'blank': 'QQ号不能为空',
        'min_length': 'QQ号最少为5位',
        'max_length': 'QQ号最多为11位',
        'invalid': 'QQ号格式不正确'
    }

    def __init__(self, **kwargs):
        kwargs.update({
            'min_length': 5,
            'max_length': 11
        })
        super().__init__(**kwargs)
        self.validators.append(self.qq_validator)

    def qq_validator(self, value):
        if not re.match(r'^\d{5,11}$', value):
            self.fail('invalid', value=value)

    def to_representation(self, value):
        qq = super().to_representation(value)
        if qq and len(qq) > 6:
            qq = qq[:3] + "****" + qq[-2:]
        elif qq and len(qq) > 2:
            qq = qq[:1] + "****" + qq[-1:]
        elif qq:
            qq = "****"
        return qq


class EmailField(serializers.EmailField):
    """邮箱字段，包含脱敏功能"""
    default_error_messages = {
        'invalid': '邮箱格式不正确'
    }
    
    def mask_email(self, email):
        if not email:
            return email
        email = re.sub(r'([^@]{1})([^@]{1,})([^@]{1})@', r'\1***\3@', email)
        return email
    
    def to_representation(self, value):
        email = super().to_representation(value)
        return self.mask_email(email)


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    orid = serializers.PrimaryKeyRelatedField(
        allow_null=True, 
        source='parent', 
        queryset=models.Comment.objects.all(), 
        required=False, 
        error_messages={
            'does_not_exist': '引用的父级评论不存在'
        }
    )
    
    content = serializers.CharField(
        max_length=1000, 
        allow_blank=False, 
        error_messages={
            'blank': '评论内容不能为空',
            'max_length': '评论内容不能超过1000个字符'
        }
    )
    
    qq = QQField(required=False, allow_null=True)
    email = EmailField(required=False, allow_null=True)
    
    class Meta:
        model = models.Comment
        fields = ['id', 'content', 'datetime', 'qq', 'email', 'orid', 'parent_message', 'status']
        extra_kwargs = {
            'datetime': {'read_only': True},
            'status': {'read_only': True},  # 状态字段只读，不允许用户修改
            'parent_message': {'read_only': True},  # 父评论内容只读
        }
    
    def create(self, validated_data):
        """创建评论时，自动填充父评论内容"""
        parent = validated_data.get('parent')
        if parent:
            validated_data['parent_message'] = parent.content
        return super().create(validated_data)
    
    def validate(self, attrs):
        """验证整体数据"""
        qq = attrs.get('qq')
        email = attrs.get('email')
        
        if qq is None and email is None:
            raise serializers.ValidationError("QQ号和邮箱至少需要提供一个")
            
        return attrs
