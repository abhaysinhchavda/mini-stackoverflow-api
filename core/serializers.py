from rest_framework import serializers
from .models import Question, Answer, Vote
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']


class AnswerSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    vote_count = serializers.SerializerMethodField()

    def get_vote_count(self, obj):
        content_type = ContentType.objects.get_for_model(Answer)
        return Vote.objects.filter(
            content_type=content_type,
            object_id=obj.id
        ).aggregate(total=Sum('vote'))['total'] or 0
    
    def get_answers(self, obj):
        answers = Answer.objects.filter(question=obj)
        return AnswerSerializer(answers, many=True).data

    class Meta:
        model = Answer
        fields = ['id', 'content', 'question', 'user', 'created_at', 'is_accepted','vote_count']
        read_only_fields = ['user', 'is_accepted']


class QuestionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    vote_count = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField(read_only=True)  # Add read_only=True here

    def get_vote_count(self, obj):
        content_type = ContentType.objects.get_for_model(Question)
        return Vote.objects.filter(content_type=content_type, object_id=obj.id).aggregate(total=Sum('vote'))['total'] or 0

    def get_answers(self, obj):
        answers = Answer.objects.filter(question=obj)
        return AnswerSerializer(answers, many=True).data

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'tags',
            'user', 'created_at', 'updated_at',
            'vote_count', 'answers'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'answers']

