from django.db import models
from django.contrib.auth.models import User
import random

def generate_otp():
    return random.randint(100000, 999999)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)


class MCQQuestion(models.Model):
        subject = models.CharField(max_length=100)
        question_text = models.TextField()
        options = models.JSONField()  # {"A": "Option A", "B": "Option B", ...}
        correct_answer = models.CharField(max_length=1)  # "A", "B", etc.

        def __str__(self):
            return self.question_text



# models.py

class SubjectiveQuestion(models.Model):
    question_text = models.TextField()
    marks = models.IntegerField(default=10)

    def __str__(self):
        return self.question_text


#user mcqs performance save
from django.db import models
from django.contrib.auth.models import User

class MCQTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    performance = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject} - {self.score}/{self.total_questions}"
#essay performance

class EssayResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.TextField()
    essay_text = models.TextField()
    score = models.IntegerField()
    performance = models.CharField(max_length=50)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic[:30]} - {self.score}/40"
#subjective performance

class SubjectiveTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test_title = models.CharField(max_length=255)
    user_answers = models.TextField()
    ai_feedback = models.TextField()
    score = models.IntegerField()
    performance = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test_title} - {self.score}"



# backend/accounts/models.py

from django.db import models
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title








#admin site models
# myapp/models.py
# In accounts/models.py
from django.db import models

class ClassSessionData(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meet_link = models.URLField()
    scheduled_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
