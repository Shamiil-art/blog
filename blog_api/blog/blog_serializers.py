from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text", "created_at", "post", "author"]
        read_only_fields = ["created_at", "author"]

    def validate_text(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Text cannot be empty.")
        if len(value) > 500:
            raise serializers.ValidationError("Text cannot exceed 500 characters.")
        return value

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "content", "created_at", "author", "comments"]
        read_only_fields = ["created_at", "author"]

    def validate_title(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 100:
            raise serializers.ValidationError("Title cannot exceed 100 characters.")
        return value

    def validate_content(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Content cannot exceed 1000 characters.")
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if len(value) > 50:
            raise serializers.ValidationError("Username cannot exceed 50 characters.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"]
        )
        return user