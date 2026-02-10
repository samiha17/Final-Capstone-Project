from django.urls import reverse
from django.test import TestCase
from .models import CustomUser, Article, Publisher


class ArticleHTMLTest(TestCase):
    def setUp(self):
        # Users
        self.reader = CustomUser.objects.create_user(
            username="reader", password="readerpass", role="reader"
        )
        self.journalist = CustomUser.objects.create_user(
            username="journalist", password="journalistpass", role="journalist"
        )
        self.editor = CustomUser.objects.create_user(
            username="editor", password="editorpass", role="editor"
        )

        # Publisher
        self.publisher = Publisher.objects.create(name="Tech Daily")
        self.publisher.journalists.add(self.journalist)

        # Articles
        self.article = Article.objects.create(
            title="Test Article",
            content="Test content",
            author=self.journalist,
            approved=False,
            publisher=self.publisher,
        )
        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="Approved content",
            author=self.journalist,
            approved=True,
            publisher=self.publisher,
        )

    # Reader can see only approved articles
    def test_reader_can_view_articles(self):
        self.client.login(username="reader", password="readerpass")
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Approved Article")
        self.assertNotContains(response, "Test Article")

    # Journalist can create article
    def test_journalist_can_create_article(self):
        self.client.login(username="journalist", password="journalistpass")
        url = reverse("article-create")
        data = {
            "title": "New Article",
            "content": "Some content",
            "publisher": self.publisher.id,
        }
        response = self.client.post(url, data)
        # CreateView redirects on success
        self.assertEqual(response.status_code, 302)
        new_article = Article.objects.get(title="New Article")
        self.assertEqual(new_article.author, self.journalist)

    # Editor can approve article
    def test_editor_can_approve_article(self):
        self.client.login(username="editor", password="editorpass")
        self.article.approved = True
        self.article.save()
        self.article.refresh_from_db()
        self.assertTrue(self.article.approved)
