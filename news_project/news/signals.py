from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser, Article
from django.core.mail import send_mail
from .utils import Tweet


# Assign group to new users
@receiver(post_save, sender=CustomUser)
def assign_group(sender, instance, created, **kwargs):
    """
    Automatically assign a new user to a group based on their role.
    """
    if created:
        group, _ = Group.objects.get_or_create(name=instance.role.capitalize())
        instance.groups.add(group)


# Handle article approval
@receiver(post_save, sender=Article)
def article_approval_handler(sender, instance, created, **kwargs):
    """
    When an article is approved:
    - Notify all subscribers of the journalist or publisher.
    - Post the article title to X (Twitter).
    """
    if instance.approved and not created:

        # Notify subscribers via email
        subscribers = CustomUser.objects.filter(
            subscriptions_journalists=instance.author
        )
        recipient_list = [user.email for user in subscribers if user.email]

        if recipient_list:
            send_mail(
                subject=f"New Article: {instance.title}",
                message=instance.content,
                from_email="news@app.com",
                recipient_list=recipient_list,
                fail_silently=False,
            )

        # Post to X (Twitter) using the Tweet class
        try:
            Tweet().make_tweet(instance.title)
        except Exception:
            pass
