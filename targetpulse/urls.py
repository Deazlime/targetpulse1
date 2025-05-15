from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('boards/', views.board_list, name='board_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-page/', views.admin_page, name='admin_page'),
    path('profile/', views.profile_view, name='profile'),
    path('company/', views.company_view, name='company'),
    path('user/<str:username>/', views.user_profile_view, name='user_profile'),
    path('boards/create/', views.board_create, name='board_create'),
    path('boards/<int:pk>/edit/', views.board_edit, name='board_edit'),
    path('boards/<int:pk>/delete/', views.board_delete, name='board_delete'),
    path('boards/<int:pk>/add_member/', views.add_member, name='add_member'),
    path('boards/<int:pk>/', views.board_detail, name='board_detail'),
    path('boards/<int:board_pk>/tasks/create/', views.task_create, name='task_create'),
    path('boards/<int:board_pk>/tasks/<int:task_pk>/edit/', views.task_edit, name='task_edit'),
    path('boards/<int:board_pk>/tasks/<int:task_pk>/delete/', views.task_delete, name='task_delete'),
    path('boards/<int:board_pk>/tasks/<int:task_pk>/change_status/', views.change_task_status, name='change_task_status'),
    path('my-tasks/', views.my_tasks_view, name='my_tasks'),
]