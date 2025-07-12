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
    return render(request, 'moderadores/listar_mascotas.html', {'mascotas': mascotas})

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
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('moderador_listar_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'moderadores/editar_mascota.html', {'form': form, 'mascota': mascota})

@login_required
def moderador_eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        return redirect('moderador_listar_mascotas')
    return render(request, 'moderadores/eliminar_mascota.html', {'mascota': mascota})
from .models import Mascota, Ubicacion
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
            data = json.loads(request.body)
            mascota = get_object_or_404(Mascota, nfc_id=data['nfc_id'])
            Ubicacion.objects.create(
                mascota=mascota,
                latitud=data['latitud'],
                longitud=data['longitud']
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


