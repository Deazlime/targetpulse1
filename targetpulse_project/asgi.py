import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import targetpulse.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'targetpulse_project.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            targetpulse.routing.websocket_urlpatterns
        )
    ),
})