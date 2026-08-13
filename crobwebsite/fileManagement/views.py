from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from .forms import UploadForm
from .models import UploadedFile
from django.contrib import messages

# Create your views here.

@login_required(login_url='login')
def fileViewPage(request):
    files = UploadedFile.objects.filter(user=request.user)
    context = {'files': files}
    return render(request, 'fileManagement/fileView.html', context)

@login_required(login_url='login')
def fileUploadPage(request):
    form = UploadForm()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user        
            upload.save()                     
            messages.success(request, 'File successfully uploaded.')
    context = {'form': form}
    return render(request, 'fileManagement/fileUpload.html', context)

@login_required(login_url='login')
def downloadFile(request, fileID):
    upload = get_object_or_404(UploadedFile, id=fileID, user=request.user)
    return FileResponse(upload.file.open('rb'), as_attachment=True)