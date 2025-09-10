from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path('admin/s3-test/', views.test_s3_connection, name='s3_test'),
]