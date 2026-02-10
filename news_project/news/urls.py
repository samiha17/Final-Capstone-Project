from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    home,
    register,
    article_list,
    subscribed_articles,
    article_detail,
    ArticleCreateView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleApproveView,
    subscribe_journalist,
    subscribe_publisher,
    editor_pending_articles,
    manage_subscriptions,
    unsubscribe_journalist,
    unsubscribe_publisher,
    NewsletterCreateView,
    NewsletterDetailView,
    NewsletterListView,
    NewsletterUpdateView,
    NewsletterDeleteView,
    ArticleApproveViewHTML,
    subscribe_journalist_html,
    subscribe_publisher_html,
    unsubscribe_journalist_html,
    unsubscribe_publisher_html,
    PublisherCreateView,
    PublisherListView,
    PublisherUpdateView,
    PublisherDeleteView,
    publisher_request_list,
    request_publisher_affiliation,
    publisher_requests_pending,
    approve_publisher_request,
)

urlpatterns = [
    # Frontend
    path("", home, name="home"),
    path("register/", register, name="register"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Articles
    path("articles/", article_list, name="article-list"),
    path("articles/subscribed/", subscribed_articles, name="subscribed-articles"),
    path("articles/<int:pk>/", article_detail, name="article-detail"),
    path("articles/create/", ArticleCreateView.as_view(), name="article-create"),
    path(
        "articles/<int:pk>/update/", ArticleUpdateView.as_view(), name="article-update"
    ),
    path(
        "articles/<int:pk>/delete/", ArticleDeleteView.as_view(), name="article-delete"
    ),
    path(
        "articles/<int:pk>/approve/",
        ArticleApproveView.as_view(),
        name="article-approve",
    ),
    # Subscriptions
    path(
        "subscribe/journalist/<int:pk>/",
        subscribe_journalist_html,
        name="subscribe-journalist",
    ),
    path(
        "subscribe/publisher/<int:pk>/",
        subscribe_publisher_html,
        name="subscribe-publisher",
    ),
    path(
        "unsubscribe/journalist/<int:pk>/html/",
        unsubscribe_journalist_html,
        name="unsubscribe-journalist-html",
    ),
    path(
        "unsubscribe/publisher/<int:pk>/html/",
        unsubscribe_publisher_html,
        name="unsubscribe-publisher-html",
    ),
    path("subscriptions/", manage_subscriptions, name="manage-subscriptions"),
    # Editor
    path(
        "editor/articles/pending/",
        editor_pending_articles,
        name="editor-pending-articles",
    ),
    # Newsletters
    path("newsletters/", NewsletterListView.as_view(), name="newsletter-list"),
    path(
        "newsletters/create/", NewsletterCreateView.as_view(), name="newsletter-create"
    ),
    path(
        "newsletters/<int:pk>/",
        NewsletterDetailView.as_view(),
        name="newsletter-detail",
    ),
    path(
        "newsletters/<int:pk>/update/",
        NewsletterUpdateView.as_view(),
        name="newsletter-update",
    ),
    path(
        "editor/articles/<int:pk>/approve/",
        ArticleApproveViewHTML.as_view(),
        name="article-approve",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        NewsletterDeleteView.as_view(),
        name="newsletter-delete",
    ),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
    path("publishers/create/", PublisherCreateView.as_view(), name="publisher-create"),
    path(
        "publishers/<int:pk>/edit/",
        PublisherUpdateView.as_view(),
        name="publisher-update",
    ),
    path(
        "publishers/<int:pk>/delete/",
        PublisherDeleteView.as_view(),
        name="publisher-delete",
    ),
    # Publisher affiliation (Journalists)
    path(
        "publishers/request/",
        publisher_request_list,
        name="publisher-request-list",
    ),
    path(
        "publishers/request/<int:pk>/",
        request_publisher_affiliation,
        name="publisher-request",
    ),
    # Publisher affiliation approval (Editors)
    path(
        "editor/publisher-requests/",
        publisher_requests_pending,
        name="publisher-requests-pending",
    ),
    path(
        "editor/publisher-requests/<int:pk>/approve/",
        approve_publisher_request,
        name="publisher-request-approve",
    ),
]
