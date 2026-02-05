from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Ticket, Departamento, Motivo, Usuario


@login_required
def lista_tickets(request):
    if request.user.rol == 'superuser':
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(usuario=request.user)

    return render(request, 'ticket_system/lista_tickets.html', {
        'tickets': tickets
    })


@login_required
def crear_ticket(request):
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        contenido = request.POST.get('contenido')
        prioridad = request.POST.get('prioridad', 'media')
        departamento_id = request.POST.get('departamento')
        motivo_id = request.POST.get('motivo')

        departamento = get_object_or_404(Departamento, id=departamento_id)
        motivo = None
        if motivo_id:
            motivo = get_object_or_404(Motivo, id=motivo_id)

        ticket = Ticket.objects.create(
            usuario=request.user,
            departamento=departamento,
            motivo=motivo,
            asunto=asunto,
            contenido=contenido,
            prioridad=prioridad
        )

        messages.success(request, f'Ticket #{ticket.id} creado exitosamente.')
        return redirect('lista_tickets')

    departamentos = Departamento.objects.filter(activo=True)
    motivos = Motivo.objects.all()

    return render(request, 'ticket_system/crear_ticket.html', {
        'departamentos': departamentos,
        'motivos': motivos
    })


@login_required
def detalle_ticket(request, ticket_id):
    if request.user.rol == 'superuser':
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = get_object_or_404(Ticket, id=ticket_id, usuario=request.user)

    if request.method == 'POST' and request.user.rol == 'superuser':
        estado = request.POST.get('estado')
        if estado:
            ticket.estado = estado
            if estado == 'cerrado':
                ticket.fecha_cierre = timezone.now()
            ticket.save()
            messages.success(request, 'Estado del ticket actualizado.')
            return redirect('detalle_ticket', ticket_id=ticket.id)

    return render(request, 'ticket_system/detalle_ticket.html', {
        'ticket': ticket
    })
