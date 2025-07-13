
from rest_framework import serializers
from . import models

_verr = serializers.ValidationError
def raise_verr(msg: str, status = 400):
    raise _verr(detail=msg, code=status)

_departments = models.EnrollModel.departments
class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnrollModel
        exclude = ['status']
        # we have made comment as blank=True
        # so comment is not required when POST
    code = serializers.IntegerField(
        help_text=models.CODE_HELP_TEXT, write_only=True)
    department = serializers.CharField()  # make input as `str`,
                                          # see validate_department
    def to_representation(self, instance: models.EnrollModel):
        """restore department to str"""
        d_ord = instance.department
        ret = super().to_representation(instance)
        ret['department'] = _departments[d_ord]
        return ret
    def validate_department(self, data: str):
        idx = -1
        if data.isdigit():
            idx = int(data)
        else:
            for (i, n) in models.EnrollModel.departments:
                if n == data:
                    idx = i
            if idx == -1:
                raise_verr(repr(data)+" is not a valid choice.")
        return idx
    def validate(self, attrs):
        email = attrs['email']
        obj = models.VerifyCodeModel.objects.filter(email=email).first()
        if obj is None:
            raise_verr(
                "no verfication code for your email currently",
                404)
        if obj.try_remove_if_unalive(): #type: ignore # we know it's non-None
            raise_verr(
                "the verfication code for your account has been outdated",
                410)
        code = obj.code #type: ignore
        if code != attrs['code']:
            raise_verr(
                "email verification code is wrong", 400)
        del attrs['code']
        return super().validate(attrs)
