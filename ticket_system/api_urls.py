from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    login_view,
    logout_view,
    DepartamentoViewSet,
    MotivoViewSet,
    TicketViewSet
)

router = DefaultRouter()
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'motivos', MotivoViewSet)
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('login/', login_view, name='api_login'),
    path('logout/', logout_view, name='api_logout'),
    path('', include(router.urls)),
]
