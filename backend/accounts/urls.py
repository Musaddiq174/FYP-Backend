from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import SendOTPView, ResetPasswordWithOTPView
from .views import GenerateTestView
from .views import GenerateEssayTestView
from .views import GenerateSubjectiveTestView
from .views import EvaluateEssayView
from .views import EvaluateMCQsAIView
from .views import EvaluateSubjectiveTestView
from .views import AdminDashboardSummaryView
from .views import UserManagementView
from .views import SubjectManagementView
from .views import QuestionManagementView
from .views import ChatbotView
from .views import adminRegisterView
from .views import evaluate_test
from .views import AdminLoginView
from .views import VideoUploadView
from .views import VideoListView
from .views import VideoDeleteView
from django.conf import settings
from django.conf.urls.static import static
from .views import UploadMeetLinkView,MeetLinksListView
from .views import DeleteClassSessionView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('reset-password/', ResetPasswordWithOTPView.as_view(), name='reset-password'),
    #using model
    path('generate-mcqs/', GenerateTestView.as_view(), name='generate-mcqs'),
    path('generate-essay/', GenerateEssayTestView.as_view(), name='generate-essay'),
    path('generate-subjective/', GenerateSubjectiveTestView.as_view(), name='generate-subjective'),
    path('evaluate-mcq-ai/', EvaluateMCQsAIView.as_view(), name='evaluate-mcq-ai'),
    path('evaluate-essay/', EvaluateEssayView.as_view(), name='evaluate-essay'),
    path('evaluate-subjective/', EvaluateSubjectiveTestView.as_view(), name='evaluate-subjective'),
    #admin site urls
    path("admin/dashboard/summary/", AdminDashboardSummaryView.as_view(), name="admin-summary"),
    path("admin/users/", UserManagementView.as_view(), name="admin-users"),
    path("admin/subjects/", SubjectManagementView.as_view(), name="admin-subjects"),
    path("admin/questions/", QuestionManagementView.as_view(), name="admin-questions"),
    #chatbot
    path("chatbot/", ChatbotView.as_view(), name="chatbot"),
    path('evaluate/', evaluate_test, name='evaluate_test'),
    path('admin-register/', adminRegisterView.as_view(), name='register'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('upload-video/', VideoUploadView.as_view(), name='upload-video'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('videos/delete/<int:video_id>/', VideoDeleteView.as_view(), name='video-delete'),
    path('upload-meet-link/', UploadMeetLinkView.as_view(), name='upload-meet-link'),
    path('meet-links/', MeetLinksListView.as_view(), name='meet-links'),
    path('class-session/delete/<int:session_id>/', DeleteClassSessionView.as_view(),
                       name='delete-session'),

              ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
