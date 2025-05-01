from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, related_name='questions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=255, blank=True)  # Tags as a comma-separated string
    votes = GenericRelation('Vote')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Answer(models.Model):
    content = models.TextField()
    question = models.ForeignKey('Question', related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    votes = GenericRelation('Vote')

    class Meta:
        unique_together = ('question', 'is_accepted')  # Only one accepted answer per question

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=[(1, 'Upvote'), (-1, 'Downvote')])

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    


