import os

from django.conf import settings
from django import forms
from .models import UploadedFile


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['title', 'file']

    def clean_file(self):
        file = self.cleaned_data['file']

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file.size > max_bytes:
            raise forms.ValidationError(
                f'File is too large ({file.size / (1024 * 1024):.1f} MB). '
                f'Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB.'
            )

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            allowed = ', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)
            raise forms.ValidationError(
                f'"{ext}" files are not allowed. Allowed types: {allowed}'
            )

        return file


class EditUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['title']