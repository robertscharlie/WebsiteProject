from urllib.parse import urlencode

from django.db.models import Case, When, Value, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import TodoItem
from .forms import TodoItemForm

SORT_OPTIONS = {
    'due': ('completed', 'dueDate'),
    'priority': ('completed', 'priority_order', 'dueDate'),
    'updated': ('-updatedAt',),
}


def _filters_querystring(request):
    """Carries the current search/status/sort filters through non-GET actions."""
    params = {}
    for key in ('q', 'status', 'sort'):
        value = request.POST.get(key) or request.GET.get(key)
        if value:
            params[key] = value
    return urlencode(params)


def _redirect_to_todo(request):
    query = _filters_querystring(request)
    url = reverse('todo:todo')
    return redirect(f"{url}?{query}" if query else url)


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
        return _redirect_to_todo(request)
    elif request.method == 'POST':
        # New todo item submission
        form = TodoItemForm(request.POST)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user
            todo_item.save()
            return _redirect_to_todo(request)

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'all')
    sort = request.GET.get('sort', 'due')
    if sort not in SORT_OPTIONS:
        sort = 'due'

    todos = TodoItem.objects.filter(user=request.user)
    if query:
        todos = todos.filter(title__icontains=query)
    if status == 'active':
        todos = todos.filter(completed=False)
    elif status == 'completed':
        todos = todos.filter(completed=True)

    if sort == 'priority':
        priority_case = Case(
            *[When(priority=key, then=Value(order)) for key, order in TodoItem.PRIORITY_ORDER.items()],
            default=Value(len(TodoItem.PRIORITY_ORDER)),
            output_field=IntegerField(),
        )
        todos = todos.annotate(priority_order=priority_case)
    todos = todos.order_by(*SORT_OPTIONS[sort])

    context = {
        'todos': todos,
        'form': form,
        'query': query,
        'status': status,
        'sort': sort,
        'now': timezone.now(),
    }
    return render(request, 'todo/todo.html', context)

@login_required(login_url='login')
def todoEdit(request, pk):
    todoItem = get_object_or_404(TodoItem, pk=pk, user=request.user)
    form = TodoItemForm(instance=todoItem)
    if request.method == 'POST':
        form = TodoItemForm(request.POST, instance=todoItem)
        if form.is_valid():
            form.save()
            return _redirect_to_todo(request)
    context = {'form': form, 'todoItem': todoItem}
    return render(request, 'todo/todoEdit.html', context)

@login_required(login_url='login')
@require_POST
def todoDelete(request, pk):
    todoItem = get_object_or_404(TodoItem, pk=pk, user=request.user)
    todoItem.delete()
    return _redirect_to_todo(request)