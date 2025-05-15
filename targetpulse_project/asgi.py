import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from targetpulse.routing import websocket_urlpatterns
import targetpulse.routing  # Убедись, что импортируется

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'targetpulse_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})