from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "seller",
            "alojamientos",
            "actividades",
            "restaurantes",
            "planings",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, required=False)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    seller = serializers.BooleanField(required=False, default=False)
    alojamientos = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    actividades = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    restaurantes = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password2",
            "name",
            "first_name",
            "last_name",
            "seller",
            "alojamientos",
            "actividades",
            "restaurantes",
        ]

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("El email es obligatorio.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return email

    def validate(self, attrs):
        if attrs.get("password2") and attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("name", "").strip()
        first_name = validated_data.pop("first_name", "").strip() or ""
        last_name = validated_data.pop("last_name", "").strip() or ""
        seller = validated_data.pop("seller", False)
        alojamientos = validated_data.pop("alojamientos", [])
        actividades = validated_data.pop("actividades", [])
        restaurantes = validated_data.pop("restaurantes", [])
        validated_data.pop("password2", None)

        email = validated_data["email"]
        username = email

        if name:
            parts = name.split(" ", 1)
            first_name = first_name or parts[0]
            last_name = last_name or (parts[1] if len(parts) > 1 else "")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
            seller=seller,
            alojamientos=alojamientos,
            actividades=actividades,
            restaurantes=restaurantes,
        )
        return user


class UpdateProfileSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    seller = serializers.BooleanField(required=False)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return email

    def update(self, instance, validated_data):
        name = validated_data.get("name", "").strip()
        if name:
            parts = name.split(" ", 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ""

        if "email" in validated_data:
            instance.email = validated_data["email"]
            instance.username = validated_data["email"]

        if "seller" in validated_data:
            instance.seller = validated_data["seller"]

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
