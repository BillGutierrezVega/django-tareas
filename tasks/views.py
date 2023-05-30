from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from .form import TaskForm
from .models import Task

SIGNUP = "signup.html"
CREATE_TASK = "create_task.html"


# Create your views here.
def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "GET":
        return render(request, SIGNUP, {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    username=request.POST["username"],
                    password=request.POST["password1"],
                )
                user.save()
                login(request, user)
                return redirect("tasks")
            except IntegrityError:
                return render(
                    request,
                    SIGNUP,
                    {
                        "form": UserCreationForm,
                        "error": "El usuario ya existe",
                    },
                )
        else:
            return render(
                request,
                SIGNUP,
                {"form": UserCreationForm, "error": "Las contraseñas no coinciden"},
            )


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, "tasks.html", {"tasks":tasks})


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, "tasks.html", {"tasks":tasks})


@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, CREATE_TASK, {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect("tasks")
        except ValueError:
            return render(
                request,
                CREATE_TASK,
                {"form": TaskForm, "error": "Tarea no creada, ingrese valores válidos"},
            )


@login_required
def task_detail(request, task_id):
    try:
        if request.method == "GET":
            tasks = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(instance=tasks)
            return render(request, "task_detail.html", {"tasks": tasks, "form": form})
        else:
            tasks = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=tasks)
            form.save()
            return redirect("tasks")
    except ValueError:
        return render(
            request,
            'task_detail.html',
            {"tasks": tasks, "form": TaskForm, "error": "Tarea no creada, ingrese valores válidos"},
        )


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect("tasks")


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect("tasks")


@login_required
def cerrar_secion(request):
    logout(request)
    return redirect("home")


def signin(request):
    if request.method == "GET":
        return render(request, "signin.html", {"form": AuthenticationForm})
    else:
        user = authenticate(
            username=request.POST["username"], password=request.POST["password"]
        )
        if user is None:
            return render(
                request,
                "signin.html",
                {
                    "form": AuthenticationForm,
                    "error": "Usuario o contraseña incorrectos",
                },
            )
        else:
            login(request, user)
            return redirect("tasks")
