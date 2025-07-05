import os

from django.http import FileResponse
from django.shortcuts import render

from .form import FileUploadForm, DownloadForm
from .models import FileUpload


def index(request):
    return render(request, 'fileupload/index.html')


def upload_file(request):
    if request.GET.get('refresh') == '1':
        form = FileUploadForm()
        return render(request, 'fileupload/upload.html', {'form': form})

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            return render(request, 'fileupload/upload_success.html', {'file_id': file.id})
        # Form is invalid (including CAPTCHA errors)
        return render(request, 'fileupload/upload.html', {'form': form})

    # GET request
    form = FileUploadForm()
    return render(request, 'fileupload/upload.html', {'form': form})

def download_file(request):
    if request.GET.get('refresh') == '1':
        form = DownloadForm()
        return render(request, 'fileupload/download.html', {'form': form})

    if request.method == 'POST':
        form = DownloadForm(request.POST)

        if form.is_valid():
            file_id = form.cleaned_data['file_id']

            try:
                file = FileUpload.objects.get(id=file_id)
                response = FileResponse(file.file)
                response['Content-Disposition'] = f'attachment; filename="{file.name}"'

                # Delete the file after download
                file.delete()
                file_path = file.file.path

                if os.path.exists(file_path):
                    os.remove(file_path)

                return response
            except (Exception, FileUpload.DoesNotExist):
                form.add_error('file_id', 'File not found')
    else:
        form = DownloadForm()
    return render(request, 'fileupload/download.html', {'form': form})


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)
