from django.shortcuts import render
from rest_framework import viewsets, filters, status, permissions, viewsets, generics
from .models import Question, Answer, UserProfile, User, Vote
from .serializers import QuestionSerializer, AnswerSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import NotFound
from oauth2_provider.models import AccessToken, RefreshToken


############ Task 2 - User Registration & Profile

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Create the user first without the password
        user = serializer.save()
        
        # Hash the password provided in the request using Django's set_password method
        user.set_password(self.request.data['password'])
        
        # Save the user object with the hashed password
        user.save()


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.userprofile
        except:
            return Response({"error": "UserProfile does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'username': user.username,
            'email': user.email,
            'reputation': profile.reputation,
        })


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Get access token from the request
            token = request.auth

            # Revoke access and refresh tokens
            if token:
                access_token = AccessToken.objects.get(token=token)
                RefreshToken.objects.filter(access_token=access_token).delete()
                access_token.delete()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

        except AccessToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


############ Task 3 - Question ViewSet

class QuestionPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags']  # Enables ?tags=some-tag filtering
    search_fields = ['title', 'tags']
    ordering_fields = ['created_at']
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to create a question

    def perform_create(self, serializer):
        # Automatically associate the logged-in user with the question
        serializer.save(user=self.request.user)  # 'user' is automatically populated from the logged-in user

    def perform_update(self, serializer):
        # Optionally, you can add custom logic for updates, like logging or adding a new field
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'error': 'You can only delete your own questions.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        return self._vote_on_object(request, self.queryset.model, pk)

    def _vote_on_object(self, request, model, pk):
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=404)

        vote_value = int(request.data.get('vote', 0))
        if vote_value not in [1, -1]:
            return Response({'error': 'Vote must be 1 or -1'}, status=400)

        content_type = ContentType.objects.get_for_model(model)

        vote, created = Vote.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.id,
            defaults={'vote': vote_value}
        )

        total_votes = Vote.objects.filter(content_type=content_type, object_id=obj.id).aggregate(total=Sum('vote'))['total'] or 0

        return Response({'status': 'Vote recorded', 'vote': vote.vote, 'total_votes': total_votes})


############ Task 4 - Answer ViewSet

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        answer = serializer.save(user=self.request.user)

        # Get the question associated with the answer
        question = answer.question

        # Send an email to the question author notifying them of the new answer
        if question.user != answer.user:  # Avoid notifying the answer author
            send_mail(
                'New Answer Posted on Your Question',
                f'Hello {question.user.username},\n\nA new answer has been posted on your question titled "{question.title}".',
                settings.DEFAULT_FROM_EMAIL,
                [question.user.email],
            )

    def get_queryset(self):
        # Allow read access to everyone, but write access only to answer owners
        if self.request.method in permissions.SAFE_METHODS:
            return Answer.objects.all()
        return Answer.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'error': 'You can only delete your own answers.'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        try:
            answer = self.get_object()  # This retrieves the answer by pk (ID)
        except Answer.DoesNotExist:
            raise NotFound({"detail": "Answer not found."})

        question = answer.question

        # Only the question author can accept an answer
        if question.user != request.user:
            return Response({"error": "Only the question author can accept an answer."}, status=status.HTTP_403_FORBIDDEN)

        # Unset any previously accepted answer for the same question
        Answer.objects.filter(question=question, is_accepted=True).update(is_accepted=False)

        # Set this answer as accepted
        answer.is_accepted = True
        answer.save()

        # Notify the answer author when their answer is accepted
        send_mail(
            'Your Answer Has Been Accepted',
            f'Hello {answer.user.username},\n\nYour answer to the question "{question.title}" has been marked as accepted by the question author.\n\nRegards,\nYour QA Platform',
            settings.DEFAULT_FROM_EMAIL,
            [answer.user.email],
        )

        return Response({"status": "Answer marked as accepted."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        return self._vote_on_object(request, self.queryset.model, pk)

    def _vote_on_object(self, request, model, pk):
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=404)

        vote_value = int(request.data.get('vote', 0))
        if vote_value not in [1, -1]:
            return Response({'error': 'Vote must be 1 or -1'}, status=400)

        content_type = ContentType.objects.get_for_model(model)

        vote, created = Vote.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.id,
            defaults={'vote': vote_value}
        )

        total_votes = Vote.objects.filter(content_type=content_type, object_id=obj.id).aggregate(total=Sum('vote'))['total'] or 0

        return Response({'status': 'Vote recorded', 'vote': vote.vote, 'total_votes': total_votes})

