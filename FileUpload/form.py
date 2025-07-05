from django import forms
from .models import FileUpload
from captcha.fields import CaptchaField


class FileUploadForm(forms.ModelForm):
    captcha = CaptchaField(
        label='Verification',
        help_text='Enter the letters/numbers shown in the image'
    )

    class Meta:
        model = FileUpload
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({
            'accept': '*/*',  # Accept all file types
        })

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name = self.cleaned_data['file'].name
        instance.size = self.cleaned_data['file'].size
        instance.mime_type = self.cleaned_data['file'].content_type

        if commit:
            instance.save()

        return instance


class DownloadForm(forms.Form):
    file_id = forms.CharField(
        label='File ID',
        max_length=36,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the file ID you received',
            'autocomplete': 'off'
        })
    )
    captcha = CaptchaField(
        label='Verification',
        help_text='Enter the letters/numbers shown in the image'
    )
