from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from .models import Certificate, InviteToken, PrivateKey, CustomUser,Team, UploadedFile, UserProfile, Website
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from django.contrib.auth import authenticate

User = get_user_model()

class TeamMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    teams = TeamMiniSerializer(many=True, read_only=True)
    class Meta:
        model= CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_admin', 'teams']
        extra_kwargs = {"password": {"write_only":True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def get_is_admin(self, obj):
        return obj.is_staff

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect credentials')

class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'name', 'members']

class TeamDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'members']

class CertificateMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'name', 'not_after', 'subject']  

class WebsiteSerializer(serializers.ModelSerializer):
    certificate = CertificateMiniSerializer(read_only=True)
    class Meta:
        model = Website
        fields = ['id', 'url', 'domain', 'certificate']
        read_only_fields = ['id', 'domain']
        
class CertificateSerializer(serializers.ModelSerializer):
    access_teams= TeamSerializer(many=True, read_only=True)
    websites     = WebsiteSerializer(many=True, read_only=True)
    has_private_key = serializers.SerializerMethodField()
    class Meta:
        model = Certificate
        fields = '__all__'
    def get_has_private_key(self, obj):
        return obj.has_private_key

class CertificateMetaSerializer(serializers.Serializer):
    file = serializers.IntegerField()
    name = serializers.CharField(max_length=255, allow_blank=True, required=False)
    teams = serializers.ListField(child=serializers.IntegerField(), required=True)
    password = serializers.CharField(required=False, allow_blank=True)
    certificate_id = serializers.IntegerField(required=False)

class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields =['id','file','uploaded_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return UploadedFile.objects.create(**validated_data)


class PrivateKeyDetailSerializer(serializers.ModelSerializer):
    certificate = CertificateMiniSerializer(read_only=True)
    access_teams= TeamSerializer(many=True, read_only=True)
    class Meta:
        model = PrivateKey
        fields = '__all__'


class PrivateKeyUploadSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    key_file = serializers.FileField()
    certificate_id = serializers.IntegerField(required=False)
    password = serializers.CharField(required=False, allow_blank=True)


class UploadedFileProcessSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    teams = serializers.ListField(child=serializers.IntegerField(), required=True)
    password = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)


class CertificateUpdateSerializer(serializers.ModelSerializer):
    access_teams = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), many=True, required=False)

    class Meta:
        model = Certificate
        fields = ['name', 'access_teams', 'comment']
    
    def upadte (self,instance,validated_data):
        teams_data = validated_data.pop('access_teams', None)
        instance = super().update(instance, validated_data)
        if teams_data is not None:
            instance.access_teams.set(teams_data)
        instance.save()
        return instance

class PrivateKeyUpdateSerializer(serializers.ModelSerializer):
    access_teams = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), many=True, required=False)
    certificate = serializers.PrimaryKeyRelatedField(queryset=Certificate.objects.all(), required=False)

    class Meta:
        model = PrivateKey
        fields = ['name', 'comment', 'access_teams', 'certificate']

    def update(self, instance, validated_data):
        teams_data = validated_data.pop('access_teams', None)
        cert_data = validated_data.pop('certificate', None)

        instance = super().update(instance, validated_data)

        if teams_data is not None:
            instance.access_teams.set(teams_data)

        if cert_data is not None:
            instance.certificate = cert_data

        instance.save()
        return instance

class AdminUserCreateSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(write_only=True, required=False)
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_admin']

    def create(self, validated_data):
        is_admin = validated_data.pop("is_admin", False)
        user = CustomUser.objects.create_user(**validated_data)
        user.is_staff = is_admin
        user.save()
        return user
    
class AdminUserUpdateSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ["email", "username", "first_name", "last_name", "is_admin"]

    def update(self, instance, validated_data):
        is_admin = validated_data.pop("is_admin", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if is_admin is not None:
            instance.is_staff = is_admin
        instance.save()
        return instance
    
class RegistrationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    email = serializers.EmailField(read_only=True)  # shown, not typed
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_token(self, value):
        try:
            invite = InviteToken.objects.get(token=value, is_used=False)
        except InviteToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invitation link.")
        self.invite = invite
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=self.invite.email,
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"]
        )
        UserProfile.objects.create(user=user)  # Default profile

        self.invite.is_used = True
        self.invite.save()
        return user
    
