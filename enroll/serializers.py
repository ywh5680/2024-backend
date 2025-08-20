from rest_framework import serializers
from . import models
from django.core.cache import cache


class VerificationCodeExpired(serializers.ValidationError):
    status_code = 410
    default_detail = "验证码已过期"


class VerificationCodeInvalid(serializers.ValidationError):
    status_code = 422
    default_detail = "验证码不正确"


class DuplicateRegistration(serializers.ValidationError):
    status_code = 409
    default_detail = "重复注册"


class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollModel
        exclude = ["status", "id"]

    code = serializers.IntegerField(help_text=models.CODE_HELP_TEXT, write_only=True)
    department = serializers.ChoiceField(
        choices=models.EnrollModel.departments,
        error_messages={"invalid_choice": "请选择一个有效的部门"},
    )

    def validate_email(self, data):
        if models.EnrollModel.objects.filter(email=data).exists():
            raise DuplicateRegistration("该邮箱已被注册")
        return data

    def validate_phone(self, data):
        if models.EnrollModel.objects.filter(phone=data).exists():
            raise DuplicateRegistration("该手机号已被注册")
        return data

    def validate_uid(self, data):
        if models.EnrollModel.objects.filter(uid=data).exists():
            raise DuplicateRegistration("该学号已被注册")
        return data

    def validate_qq(self, data):
        if models.EnrollModel.objects.filter(qq=data).exists():
            raise DuplicateRegistration("该QQ号已被注册")
        return data
    
    def validate(self, attrs):
        code = attrs.get('code')
        email = attrs.get('email')
        if code is None:
            raise serializers.ValidationError("验证码不能为空")
        
        key = f"verify_code_{email}"
        cached_code = cache.get(key)
        
        if cached_code is None:
            raise VerificationCodeExpired()
            
        if int(cached_code) != int(code):  
            raise VerificationCodeInvalid()
            
        cache.delete(key)  
        return super().validate(attrs)
    
    def create(self, validated_data):
        """创建时移除code字段，因为它不是模型字段"""
        validated_data.pop('code', None)
        return super().create(validated_data)
