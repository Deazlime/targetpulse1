from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=[
            ('В ожидании', 'В ожидании'),
            ('В работе', 'В работе'),
            ('Завершено', 'Завершено'),
        ],
        default='В ожидании'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    board = models.ForeignKey('Board', on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')], default='medium')
    deadline = models.DateField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Обычный пользователь'),
        ('manager', 'Менеджер'),
        ('developer', 'Разработчик'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"
    
class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_entries')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_spent = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.time_spent} часов"

class Board(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title