from rest_framework import serializers
from .models import Article, Newsletter, Publisher, CustomUser


# Article Serializer
class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model.
    """

    class Meta:
        model = Article
        fields = "__all__"
        read_only_fields = ["author", "approved"]


# Newsletter Serializer
class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter model.
    """

    class Meta:
        model = Newsletter
        fields = "__all__"


# Publisher Serializer
class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for Publisher model.
    """

    class Meta:
        model = Publisher
        fields = "__all__"


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "role",
            "subscriptions_publishers",
            "subscriptions_journalists",
        ]
