from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    login_view,
    logout_view,
    registro_view,
    generar_pdf_estadisticas,
    generar_pdf_ticket,
    upload_image,
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
    path('registro/', registro_view, name='api_registro'),
    path('upload-image/', upload_image, name='upload_image'),
    path('reportes/pdf-estadisticas/', generar_pdf_estadisticas, name='pdf_estadisticas'),
    path('reportes/pdf-ticket/<int:ticket_id>/', generar_pdf_ticket, name='pdf_ticket'),
    path('', include(router.urls)),
]
