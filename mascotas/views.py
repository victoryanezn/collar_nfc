from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
@login_required
def moderador_listar_mascotas_ajax(request):
    mascotas = Mascota.objects.all()
    nfc_id = request.GET.get('nfc_id', '').strip()
    nombre = request.GET.get('nombre', '').strip()
    telefono = request.GET.get('telefono_dueno', '').strip()
    if nfc_id:
        mascotas = mascotas.filter(nfc_id__icontains=nfc_id)
    if nombre:
        mascotas = mascotas.filter(nombre__icontains=nombre)
    if telefono:
        mascotas = mascotas.filter(telefono_dueno__icontains=telefono)
    html = render_to_string('moderadores/_tabla_mascotas.html', {'mascotas': mascotas}, request=request)
    return JsonResponse({'html': html})
from django.contrib.auth.decorators import login_required
from .forms import MascotaForm

# CRUD para moderadores (requiere login)
@login_required
def moderador_listar_mascotas(request):
    mascotas = Mascota.objects.all()
    nfc_id = request.GET.get('nfc_id', '').strip()
    nombre = request.GET.get('nombre', '').strip()
    telefono = request.GET.get('telefono_dueno', '').strip()
    if nfc_id:
        mascotas = mascotas.filter(nfc_id__icontains=nfc_id)
    if nombre:
        mascotas = mascotas.filter(nombre__icontains=nombre)
    if telefono:
        mascotas = mascotas.filter(telefono_dueno__icontains=telefono)
    return render(request, 'moderadores/listar_mascotas.html', {
        'mascotas': mascotas,
        'nfc_id': nfc_id,
        'nombre': nombre,
        'telefono_dueno': telefono
    })

@login_required
def moderador_crear_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('moderador_listar_mascotas')
    else:
        form = MascotaForm()
    return render(request, 'moderadores/crear_mascota.html', {'form': form})

@login_required
def moderador_editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    params = request.GET.urlencode()
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            if params:
                return redirect(f"{reverse('moderador_listar_mascotas')}?{params}")
            return redirect('moderador_listar_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'moderadores/editar_mascota.html', {'form': form, 'mascota': mascota, 'params': params})

@login_required
def moderador_eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    # Captura los parámetros de búsqueda actuales
    params = request.GET.urlencode()
    if request.method == 'POST':
        mascota.delete()
        # Redirige con los mismos parámetros de búsqueda si existen
        if params:
            return redirect(f"{reverse('moderador_listar_mascotas')}?{params}")
        return redirect('moderador_listar_mascotas')
    return render(request, 'moderadores/eliminar_mascota.html', {'mascota': mascota, 'params': params})
from .models import Mascota, Ubicacion
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



def vista_nfc(request, nfc_id):
    try:
        mascota = Mascota.objects.get(nfc_id=nfc_id)
        return render(request, 'mascotas/vista_nfc.html', {'mascota': mascota})
    except Mascota.DoesNotExist:
        response = render(request, 'mascotas/no_encontrado.html', {'nfc_id': nfc_id})
        response.status_code = 404
        return response


@csrf_exempt
def guardar_ubicacion(request):
    if request.method == 'POST':
        try:
            from django.core.mail import send_mail
            data = json.loads(request.body)
            mascota = get_object_or_404(Mascota, nfc_id=data['nfc_id'])
            ubicacion = Ubicacion.objects.create(
                mascota=mascota,
                latitud=data['latitud'],
                longitud=data['longitud']
            )
            # Enviar correo al dueño (si hay email)
            if hasattr(mascota, 'email_dueno') and mascota.email_dueno:
                from django.conf import settings
                url_maps = f"https://www.google.com/maps?q={ubicacion.latitud},{ubicacion.longitud}"
                mensaje = (
                    f"Hola {mascota.nombre_dueno},\n\n"
                    f"Sabemos lo difícil que es perder a una mascota, pero queremos ayudarte a reencontrarte con {mascota.nombre}.\n\n"
                    f"Alguien ha reportado haber visto a tu mascota y compartió la siguiente ubicación:\n"
                    f"\u2022 Ubicación: {url_maps}\n"
                    f"\u2022 Fecha y hora del reporte: {ubicacion.fecha.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                    "Haz clic en el enlace para ver la ubicación en Google Maps.\n\n"
                    "Este es un mensaje automático, por favor no respondas a este correo.\n\n"
                    "¡Mucho ánimo! El equipo de Collares NFC está contigo en este momento.\n"
                )
                send_mail(
                    subject=f"[Collares NFC] ¡Nueva ubicación reportada de {mascota.nombre}!",
                    message=mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[mascota.email_dueno],
                    fail_silently=False
                )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


