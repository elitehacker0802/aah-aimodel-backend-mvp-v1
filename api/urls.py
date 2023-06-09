from django.urls import path, include
from .views import FileUploadView, AiSummarize

urlpatterns = [
    path("transcribe/", FileUploadView.as_view(), name="transcribe"),
    path("summarize/", AiSummarize.as_view(), name="aisummarize"),
]
