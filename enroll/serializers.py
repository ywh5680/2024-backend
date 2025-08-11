from rest_framework import serializers
from . import models
from django.core.cache import cache

class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollModel
        exclude = ["status", "id"]

    code = serializers.IntegerField(help_text=models.CODE_HELP_TEXT, write_only=True)
    department = serializers.ChoiceField(
        choices=models.EnrollModel.departments,
        source="get_department_display",
        error_messages={"invalid_choice": "请选择一个有效的部门"},
    )

    def validate_email(self, data):
        if models.EnrollModel.objects.filter(email=data).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return data

    def validate_phone(self, data):
        if models.EnrollModel.objects.filter(phone=data).exists():
            raise serializers.ValidationError("该手机号已被注册")
        return data

    def validate_uid(self, data):
        if models.EnrollModel.objects.filter(uid=data).exists():
            raise serializers.ValidationError("该学号已被注册")
        return data

    def validate_qq(self, data):
        if models.EnrollModel.objects.filter(qq=data).exists():
            raise serializers.ValidationError("该QQ号已被注册")
        return data
    
    def validate(self, attrs):
        code = attrs.get('code')
        email = attrs.get('email')
        if code is None:
            raise serializers.ValidationError("验证码不能为空")
        key = f"verify_code_{email}"
        if cache.get(key) != code:
            raise serializers.ValidationError("验证码不正确")
        cache.delete(key)
        return super().validate(attrs)
