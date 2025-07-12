from django import forms
from mascotas.models import Mascota

class MascotaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vacunado_rabia'].label = '¿Vacunado contra la rabia?'
    class Meta:
        model = Mascota
        fields = [
            'nfc_id',
            'nombre',
            'foto',
            'vacunado_rabia',
            'nombre_dueno',
            'rut_dueno',
            'email_dueno',
            'telefono_dueno',
        ]
