from django.urls import path
from .views import task_list, add_task

urlpatterns = [
    path('', task_list, name='task_list'),  # 할 일 목록 페이지
    path('add/', add_task, name='add_task'),  # 할 일 추가 페이지
]
