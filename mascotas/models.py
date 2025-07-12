from django.db import models



import os
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Mascota(models.Model):
    nfc_id = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='fotos_mascotas/')
    vacunado_rabia = models.BooleanField(default=False)
    nombre_dueno = models.CharField(max_length=100)
    rut_dueno = models.CharField(max_length=15, verbose_name='RUT del dueño')
    email_dueno = models.EmailField(max_length=254, verbose_name='Correo del dueño')
    telefono_dueno = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.nfc_id})"

# Borrar la foto del sistema de archivos cuando se elimina la mascota
@receiver(post_delete, sender=Mascota)
def eliminar_foto_mascota(sender, instance, **kwargs):
    if instance.foto and instance.foto.name:
        foto_path = instance.foto.path
        if os.path.isfile(foto_path):
            os.remove(foto_path)



class Ubicacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
