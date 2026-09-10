from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from accounts.models import CustomUser
from accounts.tokens import get_auth_tokens_for_user, get_access_token_from_refresh_token
from accounts.utils import normalize_phone_number
from helpers.exceptions import CustomValidationException


NOT_A_MEMBER_MSG = (
    "No community membership found for this phone number or email. "
    "Book a session instead if you're not yet a member."
)


def not_a_member_exception():
    exc = CustomValidationException(msg=NOT_A_MEMBER_MSG, code=404)
    exc.detail['not_a_member'] = True
    return exc


def resolve_member_identifier_filter(identifier):
    """
    A member login identifier may be an email or a phone number.
    Returns a Q filter usable against CustomUser.
    """
    identifier = (identifier or '').strip()
    if '@' in identifier:
        return Q(email=identifier.lower())
    return Q(phone_number=normalize_phone_number(identifier))


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user using email and password
        try:
            admin = CustomUser.objects.get(email=email)
            if not admin.is_superuser:
                raise CustomValidationException(
                    msg="You do not have permission to access this resource",
                    code=401
                )
            if not check_password(password, admin.password):
                raise CustomValidationException(
                    msg="Invalid credentials provided.",
                    code=401
                )
        except CustomUser.DoesNotExist:
            raise CustomValidationException(
                msg="Admin not found.",
                code=404
            )
        
        admin.update_last_login()
        return {
            'name': admin.user_name,
            'email': admin.email,
            'id': admin.id,
            'tokens': get_auth_tokens_for_user(admin)
        }

class TokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField()

class AccessTokenResponseSerializer(serializers.Serializer):
    print("generating access token schema")
    access_token = serializers.CharField()
    name = serializers.CharField()

class AdminLoginResponseSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    id = serializers.UUIDField()
    tokens = TokenSerializer()
    print("generating admin login schema")


class AccessTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        return {
            'access_token': get_access_token_from_refresh_token(refresh_token)
        }


class CustomMemberCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[]
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'user_name',
            'email',
            'department',
            'phone_number',
            'date_of_birth',
            'tech_stack',
        ]
        extra_kwargs = {
            'user_name': {'required': True},
            'email': {'required': True},
            'department': {'required': True},
            'phone_number': {'required': True},
            'date_of_birth': {'required': True},
            'tech_stack': {'required': True},
        }

    def validate_email(self, value):
        # Only raise error if a *member* with the email exists
        if CustomUser.objects.filter(email__iexact=value, is_member=True).exists():
            raise CustomValidationException("A member with this email already exists.")
        return value

    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        attrs['user_name'] = attrs['user_name'].title()
        attrs['phone_number'] = normalize_phone_number(attrs.get('phone_number'))
        return attrs

    def create(self, validated_data):
        """
        Create a new member.
        
        If a user with the email exists, update their data and mark as member.
        If not, create a new member.
        """
        email = validated_data['email']
        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'user_name': validated_data['user_name'],
            'department': validated_data['department'],
            'phone_number': validated_data['phone_number'],
            'date_of_birth': validated_data['date_of_birth'],
            'tech_stack': validated_data['tech_stack'],
            'is_member': True
        })

        if not created:
            # Update existing user fields
            user.user_name = validated_data['user_name']
            user.department = validated_data['department']
            user.phone_number = validated_data['phone_number']
            user.date_of_birth = validated_data['date_of_birth']
            user.tech_stack = validated_data['tech_stack']
            user.is_member = True
            user.save()

        return user
    

class CaptureNonMemberDataSerializer(CustomMemberCreateSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'user_name',
            'email',
            'department',
            'phone_number',
            'date_of_birth',
            'tech_stack',
        ]
    
    def create(self, validated_data):
        """
        Capture non member data for reference
        
        If a user with the email exists, update their data.
        If not, create a new non member.
        """
        email = validated_data['email']
        user, created = CustomUser.objects.get_or_create(email=email, defaults={
            'user_name': validated_data['user_name'],
            'department': validated_data['department'],
            'phone_number': validated_data['phone_number'],
            'date_of_birth': validated_data['date_of_birth'],
            'tech_stack': validated_data['tech_stack'],
            'is_member': False
        })

        if not created:
            # Update existing user fields
            user.user_name = validated_data['user_name']
            user.department = validated_data['department']
            user.phone_number = validated_data['phone_number']
            user.date_of_birth = validated_data['date_of_birth']
            user.tech_stack = validated_data['tech_stack']
            user.is_member = False
            user.save()

        return user


class UserExistsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        try:
            member = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise CustomValidationException(
                msg="No user found with this email",
                code=404
            )

        return {
            "id": str(member.id),
            "name": member.user_name,
            "email": member.email,
            "is_member": member.is_member,
        }
    
class UserExistsResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    is_member = serializers.BooleanField()

class CustomMemberCreateResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    is_member = serializers.BooleanField()
    department = serializers.CharField()
    phone_number = serializers.CharField()
    date_of_birth = serializers.DateField()
    tech_stack = serializers.CharField()

class SetPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Member's email or phone number")
    password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        try:
            user = CustomUser.objects.get(resolve_member_identifier_filter(identifier))
        except CustomUser.DoesNotExist:
            raise not_a_member_exception()
        if not user.is_member:
            raise not_a_member_exception()
        attrs['user'] = user
        return attrs

class SetPasswordResponseSerializer(serializers.Serializer):
    msg = serializers.CharField()
    valid = serializers.BooleanField()

class CheckIfUserHasPasswordSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Member's email or phone number")

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        try:
            user = CustomUser.objects.get(resolve_member_identifier_filter(identifier))
        except CustomUser.DoesNotExist:
            raise not_a_member_exception()
        if not user.is_member:
            raise not_a_member_exception()
        attrs['user'] = user
        return attrs

class CheckIfUserHasPasswordResponseSerializer(serializers.Serializer):
    has_password = serializers.BooleanField()
    valid = serializers.BooleanField()

class MemberLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Member's email or phone number")
    password = serializers.CharField(required=True)
    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        try:
            user = CustomUser.objects.get(resolve_member_identifier_filter(identifier))
        except CustomUser.DoesNotExist:
            raise not_a_member_exception()
        else:
            if user.is_superuser or not user.is_member:
                raise not_a_member_exception()
            if not check_password(password, user.password):
                raise CustomValidationException(
                    msg="Invalid credentials provided.",
                    code=401
                )
            user.update_last_login()
            user_data = {
                'name': user.user_name,
                'role': 'member',
                'email': user.email,
                'phone_number': user.phone_number,
                'id': user.id,
            }
            return {
                'user': user_data,
                'tokens': get_auth_tokens_for_user(user)
            }


class MemberLoginResponseSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    id = serializers.UUIDField()
    tokens = TokenSerializer()

class MeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'user_name', 'email', 'phone_number', 'role', 'admin_role']
        read_only_fields = fields

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_member:
            return 'member'

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            raise CustomValidationException(
                msg="Invalid refresh token",
                code=401
            )
        return {
            'refresh_token': refresh_token
        }

class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'user_name', 'email', 'department', 'phone_number', 'date_of_birth', 'tech_stack', 'role']
        read_only_fields = fields
    
    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_member:
            return 'member'
        else:
            return 'non_member'

class LogoutResponseSerializer(serializers.Serializer):
    msg = serializers.CharField()
    valid = serializers.BooleanField()


class AccountSearchSerializer(serializers.Serializer):
    """
    Fast admin-facing phone number search across all users (members,
    non-members). Used by front-desk staff to pull up someone's
    subscription/payment status.
    """
    phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = normalize_phone_number(attrs.get('phone_number'))
        user = CustomUser.objects.filter(phone_number=phone).order_by('-created_at').first()
        if not user:
            raise CustomValidationException(
                msg="No user found with this phone number",
                code=404
            )
        attrs['user'] = user
        return attrs


class AdminCreateSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)
    admin_role = serializers.ChoiceField(choices=CustomUser.AdminRole.choices, required=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise CustomValidationException("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        return CustomUser.objects.create_admin(
            user_name=validated_data['user_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            admin_role=validated_data['admin_role'],
        )


class AdminResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_name = serializers.CharField()
    email = serializers.EmailField()
    admin_role = serializers.CharField()
    is_active = serializers.BooleanField()
    last_login = serializers.DateTimeField(allow_null=True)


class AdminDeactivateSerializer(serializers.Serializer):
    admin_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        admin_id = attrs.get('admin_id')
        request = self.context.get('request')
        try:
            admin = CustomUser.objects.get(id=admin_id, is_superuser=True)
        except CustomUser.DoesNotExist:
            raise CustomValidationException(msg="Admin not found", code=404)

        if request and str(request.user.id) == str(admin.id):
            raise CustomValidationException(msg="You cannot deactivate your own account", code=400)

        if admin.admin_role == CustomUser.AdminRole.SUPER:
            other_active_supers = CustomUser.objects.filter(
                is_superuser=True,
                admin_role=CustomUser.AdminRole.SUPER,
                is_active=True,
            ).exclude(id=admin.id)
            if not other_active_supers.exists():
                raise CustomValidationException(
                    msg="At least one active Super Admin must remain",
                    code=400
                )

        attrs['admin'] = admin
        return attrs

    def save(self):
        admin = self.validated_data['admin']
        admin.is_active = False
        admin.save()
        return admin
