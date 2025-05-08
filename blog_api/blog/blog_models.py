from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    class Meta:
        indexes = [
            models.Index(fields=["post", "author"]),
        ]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"