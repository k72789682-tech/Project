from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='tasks'),
    path('add-task/', views.add_task, name='add_task'),
    path('update-task/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('reminder/', views.reminder_view, name='reminder'),
    path('calendar-sync/', views.calendar_sync, name='calendar_sync'),
    path('logout/', views.logout_view, name='logout'),
]