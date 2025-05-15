from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notification, TimeEntry, Task
from asgiref.sync import sync_to_async

class BoardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass  # Клиент только слушает

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'created_at': event['created_at'],
        }))

class TimeTrackerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'task_{self.task_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'start_timer':
            await self.start_timer(data)
        elif action == 'stop_timer':
            await self.stop_timer(data)

    @sync_to_async
    def start_timer(self, data):
        task = Task.objects.get(id=self.task_id)
        TimeEntry.objects.create(
            task=task,
            user_id=data['user_id']
        )

    @sync_to_async
    def stop_timer(self, data):
        time_entry = TimeEntry.objects.filter(
            task_id=self.task_id,
            user_id=data['user_id'],
            is_running=True
        ).first()
        if time_entry:
            time_entry.stop_timer()
            return time_entry.duration
        return None

    async def send_time_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'time_update',
            'duration': str(event['duration'])
        }))