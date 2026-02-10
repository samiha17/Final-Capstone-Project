from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


# Custom User Model
class CustomUser(AbstractUser):
    """
    Adds a role field to distinguish between readers, journalists,
    and editors within the system.
    """

    ROLE_CHOICES = [
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    ]
    # Role assigned at registration
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subscriptions_publishers = models.ManyToManyField("Publisher", blank=True)
    subscriptions_journalists = models.ManyToManyField(
        "self", blank=True, symmetrical=False
    )


# Publisher Model
class Publisher(models.Model):
    """
    Represents a publisher.
    """

    name = models.CharField(max_length=100)

    # Editors who manage content for this publisher
    editors = models.ManyToManyField(
        CustomUser, related_name="publisher_editors", blank=True
    )

    # Journalists who write for this publisher
    journalists = models.ManyToManyField(
        CustomUser, related_name="publisher_journalists", blank=True
    )

    def __str__(self):
        return self.name


# Publisher affiliation requests
class PublisherRequest(models.Model):
    """
    Represents a request made by a journalist to be affiliated
    with a publisher.
    """

    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "journalist"},
        related_name="publisher_requests",
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="affiliation_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ("journalist", "publisher")

    def __str__(self):
        return f"{self.journalist.username} → {self.publisher.name}"


# Article Model
class Article(models.Model):
    """
    Represents a news article written by journalist.
    """

    # Article fields
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="articles"
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# Newsletter Model
class Newsletter(models.Model):
    """
    Represents a newsletter by a journalist or editor.
    It includes multiple articles.
    """

    # Newsletter fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="newsletters"
    )
    articles = models.ManyToManyField(Article, related_name="newsletters")
