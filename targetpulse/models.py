from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from django.core.mail import send_mail

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
    spent_time = models.DurationField(null=True, blank=True)
    estimated_time = models.DurationField(null=True, blank=True)

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
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    is_running = models.BooleanField(default=True)

    def stop_timer(self):
        self.end_time = timezone.now()
        self.duration = self.end_time - self.start_time
        self.is_running = False
        self.save()

    def __str__(self):
        return f"{self.task.title} - {self.duration}"

class Board(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    members = models.ManyToManyField(User, related_name='boards')

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    def __str__(self):
        return f"{self.user.username}: {self.message}"

@receiver(post_save, sender=Notification)
def send_notification_ws(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            # Можно добавить логирование, если нужно
            return
        group_name = f'notifications_{instance.user.id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': instance.message,
                'created_at': instance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

def send_task_assignment_email(task):
    if task.user and task.user.email:
        send_mail(
            subject='Вам назначена новая задача',
            message=f'Вам назначена задача: {task.title}\nОписание: {task.description}',
            from_email='noreply@targetpulse.local',
            recipient_list=[task.user.email],
            fail_silently=True,
        )

@receiver(post_save, sender=Task)
def task_assignment_email_signal(sender, instance, created, **kwargs):
    if created or 'user_id' in instance.get_deferred_fields():
        send_task_assignment_email(instance)