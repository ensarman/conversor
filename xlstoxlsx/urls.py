from django.urls import path
from . import views

app_name = 'xlstoxlsx'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('convert/', views.ConvertView.as_view(), name='convert'),
    path('download/<str:filename>', views.DownloadView.as_view(), name='download'),
]
