from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Publisher


# Custom User Registration Form
class CustomUserCreationForm(UserCreationForm):
    # Available roles a user can choose during registration
    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "password1", "password2")


# Article Create / Update Form
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "publisher"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 6}),
            "publisher": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        # Extract the user
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # If user is a journalist, only show publishers they're linked to
            if user.role == "journalist":
                publishers_qs = Publisher.objects.filter(journalists=user)
                if publishers_qs.exists():
                    self.fields["publisher"].queryset = publishers_qs
                else:
                    # If no publishers, hide the field
                    self.fields["publisher"].widget = forms.HiddenInput()
            else:
                # For editors or others, show all publishers
                self.fields["publisher"].queryset = Publisher.objects.all()


# Publisher Management Form (Editor-only)
class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ["name", "journalists", "editors"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "journalists": forms.CheckboxSelectMultiple(),
            "editors": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit assignments by role
        self.fields["journalists"].queryset = CustomUser.objects.filter(
            role="journalist"
        )
        self.fields["editors"].queryset = CustomUser.objects.filter(role="editor")
