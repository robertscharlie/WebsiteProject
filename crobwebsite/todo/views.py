from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import TodoItem
from .forms import TodoItemForm


# Create your views here.

@login_required(login_url='login')
def todoPage(request):
    form = TodoItemForm()
    if request.method == 'POST' and 'updateTodo' in request.POST:
        # Checkbox toggle submission
        todo_id = request.POST.get('todo_id')
        completed = request.POST.get('completed') == 'on'
        if todo_id and todo_id.isdigit():
            TodoItem.objects.filter(pk=todo_id, user=request.user).update(completed=completed)
        return redirect('todo:todo')
    elif request.method == 'POST':
        # New todo item submission
        form = TodoItemForm(request.POST)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user
            todo_item.save()
            return redirect('todo:todo')

    todos = TodoItem.objects.filter(user=request.user).order_by('completed', 'dueDate')
    context = {'todos': todos, 'form': form}
    return render(request, 'todo/todo.html', context)

@login_required(login_url='login')
def todoEdit(request, pk):
    todoItem = get_object_or_404(TodoItem, pk=pk, user=request.user)
    form = TodoItemForm(instance=todoItem)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=todoItem)
        if form.is_valid():
            form.save()
            return redirect('todo:todo')
    context = {'form': form, 'todoItem': todoItem}
    return render(request, 'todo/todoEdit.html', context)

@login_required(login_url='login')
@require_POST
def todoDelete(request, pk):
    todoItem = get_object_or_404(TodoItem, pk=pk, user=request.user)
    todoItem.delete()
    return redirect('todo:todo')