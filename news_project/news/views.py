from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


import requests

from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import Article, Newsletter, CustomUser, Publisher, PublisherRequest
from .serializers import ArticleSerializer, NewsletterSerializer
from .permissions import IsJournalist, IsEditor, IsReader
from .forms import CustomUserCreationForm, ArticleForm, PublisherForm
from .utils import Tweet


# Home View
def home(request):
    return render(request, "home.html")


# Register
def register(request):
    """
    Handle user registration.
    Allows users to choose a role (reader, journalist, editor).
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(
                request, "Account created successfully. You can now log in."
            )

            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def article_list(request):
    """
    Role-aware article list:
    - Readers: approved articles only
    - Journalists: all their own articles (approved + drafts)
    - Editors: all articles (approved + drafts)
    """

    user = request.user

    if user.is_authenticated:
        # Journalist: see all their own articles
        if user.role == "journalist":
            articles = Article.objects.filter(author=user).order_by("-created_at")
            mode = "journalist"

        # Editor: see EVERYTHING
        elif user.role == "editor":
            articles = Article.objects.all().order_by("-created_at")
            mode = "editor"

        # Reader: approved only
        else:
            articles = Article.objects.filter(approved=True).order_by("-created_at")
            mode = "reader"

    else:
        # Public users: approved only
        articles = Article.objects.filter(approved=True).order_by("-created_at")
        mode = "public"

    return render(
        request,
        "articles.html",
        {
            "articles": articles,
            "mode": mode,
        },
    )


# Subscribed articles
def subscribed_articles(request):
    """
    Show articles from journalists and publishers
    the reader is subscribed to.
    """
    user = request.user
    articles = Article.objects.filter(
        approved=True, author__in=user.subscriptions_journalists.all()
    ) | Article.objects.filter(
        approved=True, publisher__in=user.subscriptions_publishers.all()
    )
    return render(request, "subscribed_articles.html", {"articles": articles})


# Article page
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Unapproved article access control
    if not article.approved:
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role == "reader":
            return redirect("article-list")

        if request.user.role == "journalist" and article.author != request.user:
            return redirect("article-list")

    return render(request, "article_detail.html", {"article": article})


# Article list
class ArticleListView(generics.ListAPIView):
    """
    API endpoint:
    GET /api/articles/
    Returns approved articles (readers only).
    """

    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsReader]


# Subscribed article
class SubscribedArticleView(generics.ListAPIView):
    """
    API endpoint:
    GET /api/articles/subscribed/
    Returns articles from subscribed journalists and publishers.
    """

    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsReader]

    def get_queryset(self):
        user = self.request.user
        return Article.objects.filter(approved=True).filter(
            Q(author__in=user.subscriptions_journalists.all())
            | Q(publisher__in=user.subscriptions_publishers.all())
        )


# Article detail
class ArticleDetailView(generics.RetrieveAPIView):
    """
    API endpoint:
    GET /api/articles/<id>/
    Retrieve a single approved article.
    """

    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsReader]


# Article Create
class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Journalists can create articles.
    Publisher dropdown is filtered based on journalist affiliation.
    """

    model = Article
    form_class = ArticleForm  # Use the custom form
    template_name = "article_form.html"
    success_url = reverse_lazy("article-list")

    def get_form_kwargs(self):
        """Pass current user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == "journalist"


# Update article
class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow journalists to update their own articles, editors can update any article."""

    model = Article
    form_class = ArticleForm
    template_name = "article_form.html"
    success_url = reverse_lazy("article-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        # Editors can edit any article
        if self.request.user.role == "editor":
            return True
        # Journalists can edit only their own
        return self.get_object().author == self.request.user


# Delete Article
class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Editors can delete any article. Journalists can delete only their own articles."""

    model = Article
    template_name = "articles/article_confirm_delete.html"
    success_url = reverse_lazy("article-list")

    def test_func(self):
        # Editors can delete anything
        if self.request.user.role == "editor":
            return True
        # Journalists can delete only their own articles
        if (
            self.request.user.role == "journalist"
            and self.get_object().author == self.request.user
        ):
            return True
        return False

    def delete(self, request, *args, **kwargs):
        """Add a success message after deletion."""
        article = self.get_object()
        messages.success(
            request, f"Article '{article.title}' has been deleted successfully."
        )
        return super().delete(request, *args, **kwargs)


# Article Approval
class ArticleApproveViewHTML(View):
    """Editor approval via HTML form."""

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if article.approved:
            messages.warning(request, f"Article '{article.title}' is already approved.")
        else:
            article.approved = True
            article.save()
            messages.success(
                request, f"Article '{article.title}' approved successfully."
            )

        return redirect("/editor/articles/pending/")


# Article Approval (API)
class ArticleApproveView(generics.GenericAPIView):
    """
    API endpoint:
    POST /api/articles/<id>/approve/
    Editors approve articles and notify subscribers.
    """

    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated, IsEditor]

    def post(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response(
                {"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if article.approved:
            return Response(
                {"message": "Article already approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Approve the article
        article.approved = True
        article.save()

        # Notify subscribers via email
        recipient_emails = [
            user.email
            for user in CustomUser.objects.filter(
                subscriptions_journalists=article.author
            )
            if user.email
        ]

        if recipient_emails:
            send_mail(
                subject=f"New Article Published: {article.title}",
                message=article.content,
                from_email="news@app.com",
                recipient_list=recipient_emails,
                fail_silently=True,
            )

        # Post to X/Twitter using OAuth1
        try:
            Tweet().make_tweet(article.title)
        except Exception:
            # Don't fail approval just because X failed
            pass

        return Response(
            {"message": "Article approved and distributed."},
            status=status.HTTP_200_OK,
        )


class IsEditorOrOwner(BasePermission):
    """
    Custom permission: editors can delete any article,
    journalists can delete their own articles.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == "editor":
            return True
        if request.user.role == "journalist" and obj.author == request.user:
            return True
        return False


# Article ViewSet
class ArticleViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for articles via REST API."""

    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "reader":
            return Article.objects.filter(approved=True)
        return Article.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsJournalist()]
        elif self.action == "destroy":  # DELETE request
            return [IsAuthenticated(), IsEditorOrOwner()]
        elif self.action == "approve":
            return [IsAuthenticated(), IsEditor()]
        elif self.action == "subscribed":
            return [IsAuthenticated(), IsReader()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsEditor])
    def approve(self, request, pk=None):
        article = self.get_object()
        if article.approved:
            return Response(
                {"message": "Article already approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        article.approved = True
        article.save()
        return Response(
            {"status": "Article approved and distributed"}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], permission_classes=[IsReader])
    def subscribed(self, request):
        user = request.user
        articles = Article.objects.filter(approved=True).filter(
            Q(author__in=user.subscriptions_journalists.all())
            | Q(publisher__in=user.subscriptions_publishers.all())
        )
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [IsAuthenticated]


# Subscribe to journalist
@api_view(["POST"])
@permission_classes([IsReader])
def subscribe_journalist(request, pk):
    journalist = CustomUser.objects.get(pk=pk, role="journalist")
    request.user.subscriptions_journalists.add(journalist)
    return Response({"status": "subscribed"})


# Subscribe to publisher
@api_view(["POST"])
@permission_classes([IsReader])
def subscribe_publisher(request, pk):
    publisher = CustomUser.objects.get(pk=pk, role="publisher")
    request.user.subscriptions_publishers.add(publisher)
    return Response({"status": "subscribed"})


def is_editor(user):
    return user.is_authenticated and user.role == "editor"


@login_required
@user_passes_test(is_editor)
def editor_pending_articles(request):
    articles = Article.objects.filter(approved=False).order_by("-created_at")
    return render(
        request,
        "pending_articles.html",
        {"articles": articles},
    )


def is_reader(user):
    return user.is_authenticated and user.role == "reader"


@login_required
@user_passes_test(is_reader)
def manage_subscriptions(request):
    journalists = CustomUser.objects.filter(role="journalist")
    publishers = Publisher.objects.all()

    return render(
        request,
        "subscriptions.html",
        {
            "journalists": journalists,
            "publishers": publishers,
        },
    )


@api_view(["POST"])
@permission_classes([IsReader])
def unsubscribe_journalist(request, pk):
    journalist = CustomUser.objects.get(pk=pk, role="journalist")
    request.user.subscriptions_journalists.remove(journalist)
    return Response({"status": "unsubscribed"})


@api_view(["POST"])
@permission_classes([IsReader])
def unsubscribe_publisher(request, pk):
    publisher = CustomUser.objects.get(pk=pk, role="publisher")
    request.user.subscriptions_publishers.remove(publisher)
    return Response({"status": "unsubscribed"})


class NewsletterListView(ListView):
    """View newsletters."""

    model = Newsletter
    template_name = "newsletter_list.html"
    context_object_name = "newsletters"
    ordering = ["-created_at"]


class NewsletterDetailView(DetailView):
    """View a single newsletter."""

    model = Newsletter
    template_name = "newsletter_detail.html"
    context_object_name = "newsletter"


class NewsletterCreateView(CreateView):
    """Journalists and editors create newsletters."""

    model = Newsletter
    fields = ["title", "description", "articles"]
    template_name = "newsletter_form.html"
    success_url = reverse_lazy("newsletter-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NewsletterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow journalists to update their own newsletters, editors can update any newsletter."""

    model = Newsletter
    fields = ["title", "description", "articles"]
    template_name = "newsletter_form.html"
    success_url = reverse_lazy("newsletter-list")

    def test_func(self):
        # Editors can edit any newsletter
        if self.request.user.role == "editor":
            return True

        # Journalists can edit only their own newsletters
        return self.get_object().author == self.request.user


class NewsletterDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Allow editors to delete any newsletter.
    Journalists can delete only their own newsletters.
    """

    model = Newsletter
    success_url = reverse_lazy("newsletter-list")

    def test_func(self):
        user = self.request.user
        newsletter = self.get_object()

        # Editors can delete any newsletter
        if user.role == "editor":
            return True

        # Journalists can delete only their own newsletters
        if user.role == "journalist" and newsletter.author == user:
            return True

        return False


# Subscribe journalist (HTML)
@login_required
def subscribe_journalist_html(request, pk):
    journalist = get_object_or_404(CustomUser, pk=pk, role="journalist")
    if journalist in request.user.subscriptions_journalists.all():
        messages.info(request, f"Already subscribed to {journalist.username}.")
    else:
        request.user.subscriptions_journalists.add(journalist)
        messages.success(request, f"Subscribed to {journalist.username}!")
    return redirect("manage-subscriptions")


# Subscribe publisher (HTML)
@login_required
def subscribe_publisher_html(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscriptions_publishers.add(publisher)
    messages.success(request, f"Subscribed to {publisher.name} successfully.")
    return redirect("manage-subscriptions")


# Unsubscribe journalist (HTML)
@login_required
def unsubscribe_journalist_html(request, pk):
    journalist = get_object_or_404(CustomUser, pk=pk, role="journalist")
    if journalist in request.user.subscriptions_journalists.all():
        request.user.subscriptions_journalists.remove(journalist)
        messages.success(
            request, f"Unsubscribed from {journalist.username} successfully."
        )
    else:
        messages.warning(request, f"You were not subscribed to {journalist.username}.")
    return redirect("manage-subscriptions")


# Unsubscribe publisher (HTML)
@login_required
def unsubscribe_publisher_html(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    request.user.subscriptions_publishers.remove(publisher)
    messages.success(request, f"Unsubscribed from {publisher.name} successfully.")
    return redirect("manage-subscriptions")


# Lists all publishers in the system.
# This view is used by editors to manage publishers and their affiliations.
class PublisherListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Publisher
    template_name = "publisher_list.html"
    context_object_name = "publishers"

    def test_func(self):
        return self.request.user.role == "editor"


# Allows editors to create new publishers.
# Editors can assign journalists and other editors to a publisher here.
class PublisherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "publisher_form.html"
    success_url = reverse_lazy("publisher-list")

    def test_func(self):
        return self.request.user.role == "editor"


# Allows editors to update existing publishers.
# Editors can modify journalist and editor affiliations here.
class PublisherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publisher
    form_class = PublisherForm
    template_name = "publisher_form.html"
    success_url = reverse_lazy("publisher-list")

    def test_func(self):
        return self.request.user.role == "editor"


# Only editors can delete publishers
class PublisherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Publisher
    template_name = "publisher_confirm_delete.html"  # Create this template
    success_url = reverse_lazy("publisher-list")

    def test_func(self):
        # Only editors can delete publishers
        return self.request.user.role == "editor"


@login_required
def publisher_request_list(request):
    """
    View for journalists to see a list of publishers they are not yet affiliated with.
    """
    if request.user.role != "journalist":
        return redirect("home")

    publishers = Publisher.objects.exclude(journalists=request.user)
    return render(
        request,
        "publisher_request_list.html",
        {"publishers": publishers},
    )


@login_required
def request_publisher_affiliation(request, pk):
    """
    Handle the action of a journalist requesting affiliation with a specific publisher.
    """
    if request.user.role != "journalist":
        return redirect("home")

    publisher = get_object_or_404(Publisher, pk=pk)
    PublisherRequest.objects.get_or_create(journalist=request.user, publisher=publisher)
    messages.success(request, "Affiliation request sent.")
    return redirect("publisher-request-list")


@login_required
@user_passes_test(is_editor)
def publisher_requests_pending(request):
    """
    Editor view to see all pending publisher affiliation requests.
    """
    requests = PublisherRequest.objects.filter(approved=False)
    return render(
        request,
        "publisher_requests_pending.html",
        {"requests": requests},
    )


@login_required
@user_passes_test(is_editor)
def approve_publisher_request(request, pk):
    """
    Editor action to approve a journalist's request to join a publisher.
    Adds journalist to the publisher and marks request as approved.
    """
    req = get_object_or_404(PublisherRequest, pk=pk)
    req.publisher.journalists.add(req.journalist)
    req.approved = True
    req.save()
    messages.success(request, "Journalist added to publisher.")
    return redirect("publisher-requests-pending")
