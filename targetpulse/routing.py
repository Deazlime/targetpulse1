from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/(?P<user_id>\\d+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/task/(?P<task_id>\\d+)/timer/$', consumers.TimeTrackerConsumer.as_asgi()),
]