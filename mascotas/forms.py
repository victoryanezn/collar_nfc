from django import forms
from mascotas.models import Mascota

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nfc_id', 'nombre', 'foto', 'vacunado_rabia', 'nombre_dueno', 'telefono_dueno']
