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
        extra_kwargs = {
            'name': {
                'error_messages': {
                    'blank': '姓名不能为空',
                    'required': '姓名是必填项'
                }
            },
            'uid': {
                'error_messages': {
                    'required': '学号是必填项',
                    'invalid': '请输入有效的学号'
                }
            },
            'major': {
                'error_messages': {
                    'blank': '年级专业不能为空',
                    'required': '年级专业是必填项'
                }
            },
            'phone': {
                'error_messages': {
                    'required': '手机号码是必填项',
                    'invalid': '请输入有效的手机号码'
                }
            },
            'email': {
                'error_messages': {
                    'required': '邮箱是必填项',
                    'invalid': '请输入有效的邮箱地址'
                }
            },
            'department': {
                'error_messages': {
                    'required': '意向部门是必填项',
                    'invalid_choice': '请选择一个有效的部门'
                }
            },
            'content': {
                'error_messages': {
                    'blank': '加入理由不能为空',
                    'required': '加入理由是必填项'
                }
            },
            'qq': {
                'error_messages': {
                    'required': 'QQ号是必填项',
                    'invalid': '请输入有效的QQ号'
                }
            },
            'comment': {
                'error_messages': {
                    'blank': '备注不能为空',
                    'required': '备注是必填项'
                }
            }
        }

    code = serializers.IntegerField(
        help_text=models.CODE_HELP_TEXT, 
        write_only=True,
        error_messages={
            'required': '验证码是必填项',
            'invalid': '请输入有效的验证码'
        }
    )
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
