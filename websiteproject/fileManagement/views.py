from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UploadForm, EditUploadForm
from .models import UploadedFile
from django.contrib import messages

# Create your views here.

@login_required(login_url='login')
def fileViewPage(request):
    query = request.GET.get('q', '').strip()
    files = UploadedFile.objects.filter(user=request.user)
    if query:
        files = files.filter(title__icontains=query)
    context = {'files': files, 'query': query}
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
            return redirect('fileUploadPage')
    context = {'form': form}
    return render(request, 'fileManagement/fileUpload.html', context)

@login_required(login_url='login')
def downloadFile(request, fileID):
    upload = get_object_or_404(UploadedFile, id=fileID, user=request.user)
    return FileResponse(upload.file.open('rb'), as_attachment=True)

@login_required(login_url='login')
def fileEditPage(request, fileID):
    upload = get_object_or_404(UploadedFile, id=fileID, user=request.user)
    form = EditUploadForm(instance=upload)
    if request.method == 'POST':
        form = EditUploadForm(request.POST, instance=upload)
        if form.is_valid():
            form.save()
            messages.success(request, 'File renamed.')
            return redirect('fileViewPage')
    context = {'form': form, 'upload': upload}
    return render(request, 'fileManagement/fileEdit.html', context)

@login_required(login_url='login')
@require_POST
def fileDeletePage(request, fileID):
    upload = get_object_or_404(UploadedFile, id=fileID, user=request.user)
    upload.file.delete(save=False)
    upload.delete()
    messages.success(request, 'File deleted.')
    return redirect('fileViewPage')