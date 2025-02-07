from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from tags.models import Tag


def validate_uploaded_file(file):
    name = file.name
    if name.endswith(settings.REJECTED_FILE_FORMATS):
        raise ValidationError(
            "Les documents compressés ne sont pas supportés pour le moment."
        )


class FileForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Titre (optionnel)"}
        ),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-input", "placeholder": "Description (optionnel)"}
        ),
    )

    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "data-placeholder": "Ajoute des tags",
                "data-controller": "tom-select",
            }
        ),
    )


class UploadFileForm(FileForm):
    file = forms.FileField(
        validators=[validate_uploaded_file],
        widget=forms.FileInput(
            attrs={
                "class": "file-upload",
            }
        ),
    )


class ReUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_uploaded_file])


class MultipleUploadFileForm(UploadFileForm):
    pass
