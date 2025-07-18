from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TodoItem
from .forms import TodoItemForm
from django.shortcuts import redirect


# Create your views here.

# def fileUploadPage(request):
#     form = UploadForm()
#     if request.method == 'POST':
#         form = UploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             upload = form.save(commit=False)
#             upload.user = request.user        
#             upload.save()                     
#             messages.success(request, 'File successfully uploaded.')
#     context = {'form': form}
#     return render(request, 'fileManagement/fileUpload.html', context)


@login_required(login_url='login')
def todoPage(request):
    form = TodoItemForm()
    if request.method == 'POST':
        # Handle new todo creation
        form = TodoItemForm(request.POST)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user
            todo_item.save()
            form = TodoItemForm()
            return redirect('todo:todo')  # Refresh the page to show the new item

    # Handle checkbox update via AJAX or form submission
    if request.method == 'POST' and 'updateTodo' in request.POST:
        todo_id = request.POST.get('todo_id')
        completed = request.POST.get('completed') == 'on'
        TodoItem.objects.filter(pk=todo_id, user=request.user).update(completed=completed)
        return redirect('todo:todo')
    # DELETE ABOVE

    todos = TodoItem.objects.filter(user=request.user).order_by('completed', 'dueDate')
    context = {'todos': todos, 'form': form}
    return render(request, 'todo/todo.html', context)

@login_required(login_url='login')
def todoCreate(request):
    form = TodoItemForm()
    if request.method == 'POST':
        form = TodoItemForm(request.POST)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user
            todo_item.save()
    return render(request, 'todo/todo.html')  # Redirect or render a template after creation

@login_required(login_url='login')
def todoEdit(request, pk):
    todoItem = TodoItem.objects.get(pk=pk, user=request.user)
    form = TodoItemForm(instance=todoItem)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=todoItem)
        if form.is_valid():
            form.save()
            return redirect('todo:todo')
    context = {'form': form, 'todoItem': todoItem}
    return render(request, 'todo/todoEdit.html', context)

@login_required(login_url='login')
def todoDelete(request, pk):
    todoItem = TodoItem.objects.get(pk=pk, user=request.user)
    todoItem.delete()
    return redirect('todo:todo')