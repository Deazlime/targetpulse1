from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Task, UserProfile, Board, Notification, TimeEntry
from django import forms
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.forms import ModelForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import BoardForm, TaskForm
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods

# Форма для редактирования профиля
class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

def index_view(request):
    return render(request, 'targetpulse/index.html')

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    total_time = sum([entry.time_spent for entry in task.time_entries.all()])
    return render(request, 'targetpulse/task_detail.html', {'task': task, 'total_time': total_time})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Попытка входа с email: {email}, пароль: {password}")  # Для отладки
        user = authenticate(request, email=email, password=password)
        if user is not None:
            print(f"Пользователь аутентифицирован: {user.username}")  # Для отладки
            login(request, user)
            next_url = request.GET.get('next', 'index')  # Изменено на index
            return redirect(next_url)
        else:
            print("Аутентификация не удалась.")  # Для отладки
            return render(request, 'targetpulse/login.html', {'error': 'Неверный email или пароль'})
    return render(request, 'targetpulse/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            return render(request, 'targetpulse/register.html', {'error': 'Пароли не совпадают'})

        if User.objects.filter(email=email).exists():
            return render(request, 'targetpulse/register.html', {'error': 'Пользователь с таким email уже существует'})

        if User.objects.filter(username=username).exists():
            return render(request, 'targetpulse/register.html', {'error': 'Пользователь с таким именем уже существует'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        # Создаём UserProfile для нового пользователя
        UserProfile.objects.create(user=user)

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Изменено на index
        else:
            return render(request, 'targetpulse/register.html', {'error': 'Не удалось войти после регистрации'})

    return render(request, 'targetpulse/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_page(request):
    return render(request, 'targetpulse/admin_page.html', {'message': 'Добро пожаловать, администратор!'})

@login_required
def profile_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            if 'email' in request.POST and request.POST['email']:
                request.user.email = request.POST['email']
                request.user.save()
            # Проверяем и обновляем никнейм
            if 'username' in request.POST and request.POST['username']:
                if User.objects.filter(username=request.POST['username']).exclude(id=request.user.id).exists():
                    return render(request, 'targetpulse/profile.html', {
                        'user': request.user,
                        'profile_form': profile_form,
                        'error': 'Этот никнейм уже занят'
                    })
                request.user.username = request.POST['username']
                request.user.save()
            # Проверяем и обновляем пароль
            if 'password' in request.POST and request.POST['password']:
                request.user.set_password(request.POST['password'])
                request.user.save()
                login(request, request.user)
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=user_profile)
    
    return render(request, 'targetpulse/profile.html', {
        'user': request.user,
        'profile_form': profile_form
    })
    
@login_required
def board_list(request):
    boards = Board.objects.filter(members=request.user)
    return render(request, 'targetpulse/board_list.html', {'boards': boards})

@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.creator = request.user
            board.save()
            board.members.add(request.user)
            return redirect('board_list')
    else:
        form = BoardForm()
    return render(request, 'targetpulse/board_form.html', {'form': form})

@login_required
def board_edit(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.user != board.creator:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('board_list')
    else:
        form = BoardForm(instance=board)
    return render(request, 'targetpulse/board_form.html', {'form': form, 'edit': True})

@login_required
def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.user != board.creator:
        return HttpResponseForbidden()
    if request.method == 'POST':
        board.delete()
        return redirect('board_list')
    return render(request, 'targetpulse/board_confirm_delete.html', {'board': board})

@login_required
def add_member(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.user != board.creator:
        return HttpResponseForbidden()
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()
        if user:
            board.members.add(user)
            return redirect('board_list')
        else:
            return render(request, 'targetpulse/add_member.html', {'board': board, 'error': 'Пользователь не найден'})
    return render(request, 'targetpulse/add_member.html', {'board': board})

@login_required
def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.user not in board.members.all():
        return HttpResponseForbidden()
    tasks = board.tasks.all()
    statuses = ['В ожидании', 'В работе', 'Завершено', 'Выполнить']
    tasks_by_status = [(status, tasks.filter(status=status)) for status in statuses]
    return render(request, 'targetpulse/board_detail.html', {
        'board': board,
        'tasks_by_status': tasks_by_status,
        'statuses': statuses
    })

@login_required
def task_create(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if request.user not in board.members.all():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = TaskForm(request.POST, board=board)
        if form.is_valid():
            task = form.save(commit=False)
            task.board = board
            task.save()
            form.save_m2m()
            # Создаём уведомление, если назначен пользователь
            if task.user:
                Notification.objects.create(
                    user=task.user,
                    message=f'Вам назначена новая задача: {task.title}',
                    task=task
                )
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(board=board)
    return render(request, 'targetpulse/task_form.html', {'form': form, 'board': board})

@login_required
def task_edit(request, board_pk, task_pk):
    board = get_object_or_404(Board, pk=board_pk)
    task = get_object_or_404(Task, pk=task_pk, board=board)
    if request.user not in board.members.all():
        return HttpResponseForbidden()
    old_user = task.user
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, board=board)
        if form.is_valid():
            task = form.save()
            # Если назначение изменилось, создаём уведомление
            if task.user and task.user != old_user:
                Notification.objects.create(
                    user=task.user,
                    message=f'Вам назначена новая задача: {task.title}',
                    task=task
                )
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(instance=task, board=board)
    return render(request, 'targetpulse/task_form.html', {'form': form, 'board': board, 'edit': True})

@login_required
def task_delete(request, board_pk, task_pk):
    board = get_object_or_404(Board, pk=board_pk)
    task = get_object_or_404(Task, pk=task_pk, board=board)
    if request.user not in board.members.all():
        return HttpResponseForbidden()
    if request.method == 'POST':
        task.delete()
        return redirect('board_detail', pk=board.pk)
    return render(request, 'targetpulse/task_confirm_delete.html', {'task': task, 'board': board})

@csrf_exempt
@login_required
def change_task_status(request, board_pk, task_pk):
    if request.method == 'POST':
        board = get_object_or_404(Board, pk=board_pk)
        task = get_object_or_404(Task, pk=task_pk, board=board)
        if request.user not in board.members.all():
            return JsonResponse({'error': 'Forbidden'}, status=403)
        new_status = request.POST.get('status')
        if new_status in ['В ожидании', 'В работе', 'Завершено', 'Выполнить']:
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Invalid status'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def company_view(request):
    team_members = UserProfile.objects.all()
    return render(request, 'targetpulse/company.html', {'team_members': team_members})

@login_required
def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    return render(request, 'targetpulse/user_profile.html', {
        'profile_user': user,
        'profile': profile
    })

@login_required
def my_tasks_view(request):
    # Get all tasks assigned to the current user
    tasks = Task.objects.filter(user=request.user).order_by('-id')
    return render(request, 'targetpulse/my_tasks.html', {'tasks': tasks})

@require_POST
def start_timer(request, task_id):
    task = Task.objects.get(id=task_id)
    # Останавливаем все активные таймеры для этой задачи
    TimeEntry.objects.filter(task=task, is_running=True).update(
        end_time=timezone.now(),
        is_running=False
    )
    # Создаем новый таймер
    time_entry = TimeEntry.objects.create(
        task=task,
        user=request.user,
        start_time=timezone.now()
    )
    return JsonResponse({
        'status': 'success',
        'timer_id': time_entry.id,
        'start_time': time_entry.start_time.isoformat()
    })

@require_POST
def stop_timer(request, timer_id):
    time_entry = TimeEntry.objects.get(id=timer_id, user=request.user)
    time_entry.stop_timer()
    return JsonResponse({
        'status': 'success',
        'duration': str(time_entry.duration)
    })

@require_POST
def get_timer_status(request, task_id):
    task = Task.objects.get(id=task_id)
    active_timer = TimeEntry.objects.filter(task=task, is_running=True).first()
    if active_timer:
        return JsonResponse({
            'status': 'running',
            'timer_id': active_timer.id,
            'start_time': active_timer.start_time.isoformat()
        })
    return JsonResponse({'status': 'stopped'})

@require_http_methods(["GET"])
def get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
        task__isnull=False,
        task__in=Task.objects.all()
    ).order_by('-created_at')
    
    return JsonResponse({
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'url': f'/tasks/{n.task.id}/' if n.task else '#'
            } for n in notifications
        ],
        'total_count': notifications.count()
    })

@require_http_methods(["GET"])
def check_new_notifications(request):
    since = request.GET.get('since')
    if not since:
        return JsonResponse({'error': 'Missing since parameter'}, status=400)
        
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False,
        created_at__gt=since,
        task__isnull=False,
        task__in=Task.objects.all()
    ).order_by('-created_at')
    
    return JsonResponse({
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'url': f'/tasks/{n.task.id}/' if n.task else '#'
            } for n in notifications
        ],
        'total_count': Notification.objects.filter(user=request.user, is_read=False, task__isnull=False, task__in=Task.objects.all()).count()
    })

@csrf_exempt
@require_POST
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})

@require_POST
def set_task_status(request, task_id):
    task = Task.objects.get(id=task_id)
    status = request.POST.get('status')
    if status in ['В ожидании', 'В работе', 'Завершено']:
        task.status = status
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'error': 'Invalid status'})