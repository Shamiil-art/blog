from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


class BlogAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="otherpassword"
        )
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(
            title="Test Post",
            content="Test Content",
            author=self.user
        )
        self.comment = Comment.objects.create(
            text="Test Comment",
            post=self.post,
            author=self.user
        )

    def get_token(self, username="testuser", password="testpassword"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": password}
        )
        return response.data["access"]

    def test_register_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("user-list"),
            {"username": "newuser", "password": "newpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "newuser")

    def test_register_invalid_data(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("user-list"),
            {"username": "ab", "password": "123"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_user(self):
        self.client.force_authenticate(user=None)
        self.client.post(
            reverse("user-list"),
            {"username": "newuser", "password": "newpassword"}
        )
        response = self.client.post(
            reverse("user-list"),
            {"username": "newuser", "password": "newpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_login(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_invalid_credentials(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post(self):
        response = self.client.post(
            reverse("post-list"),
            {"title": "New Post", "content": "New Content"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Post")
        self.assertEqual(response.data["author"], self.user.id)

    def test_create_post_invalid_data(self):
        response = self.client.post(
            reverse("post-list"),
            {"title": "", "content": "a" * 1001}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("content", response.data)

    def test_create_post_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("post-list"),
            {"title": "New Post", "content": "New Content"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_posts(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Post")
        self.assertEqual(len(response.data[0]["comments"]), 1)
        self.assertEqual(response.data[0]["comments"][0]["text"], "Test Comment")

    def test_update_post(self):
        response = self.client.put(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Updated Post", "content": "Updated Content"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Post")
        self.assertEqual(response.data["content"], "Updated Content")

    def test_update_post_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Updated Post"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(
            reverse("post-detail", args=[self.post.id]),
            {"title": "Updated Post"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        response = self.client.delete(reverse("post-detail", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(len(response.data), 0)

    def test_delete_post_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse("post-detail", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(reverse("post-detail", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment(self):
        response = self.client.post(
            reverse("post-comments", args=[self.post.id]),
            {"text": "New Comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "New Comment")
        self.assertEqual(response.data["post"], self.post.id)
        self.assertEqual(response.data["author"], self.user.id)

    def test_create_comment_invalid_data(self):
        response = self.client.post(
            reverse("post-comments", args=[self.post.id]),
            {"text": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", response.data)

    def test_create_comment_invalid_post(self):
        response = self.client.post(
            reverse("post-comments", args=[999]),
            {"text": "New Comment"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_comments(self):
        response = self.client.get(reverse("post-comments", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["text"], "Test Comment")

    def test_get_comments_invalid_post(self):
        response = self.client.get(reverse("post-comments", args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment(self):
        response = self.client.put(
            reverse("comment-detail", args=[self.comment.id]),
            {"text": "Updated Comment", "post": self.post.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "Updated Comment")

    def test_update_comment_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(
            reverse("comment-detail", args=[self.comment.id]),
            {"text": "Updated Comment", "post": self.post.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(
            reverse("comment-detail", args=[self.comment.id]),
            {"text": "Updated Comment", "post": self.post.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment(self):
        response = self.client.delete(
            reverse("comment-detail", args=[self.comment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(reverse("post-comments", args=[self.post.id]))
        self.assertEqual(len(response.data), 0)

    def test_delete_comment_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(
            reverse("comment-detail", args=[self.comment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_not_owner(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(
            reverse("comment-detail", args=[self.comment.id])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_isolation(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        response = self.client.get(reverse("post-comments", args=[self.post.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)