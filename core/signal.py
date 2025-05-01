from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Answer
from django.core.mail import send_mail

@receiver(post_save, sender=Answer)
def notify_question_author_on_new_answer(sender, instance, created, **kwargs):
    if created:
        question_author = instance.question.user
        answer_author = instance.user

        if question_author != answer_author:
            send_mail(
                subject='New Answer to Your Question',
                message=f'Your question "{instance.question.title}" has a new answer.',
                from_email='noreply@example.com',
                recipient_list=[question_author.email],
                fail_silently=True,
            )
