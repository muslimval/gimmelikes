from django.shortcuts import render

# Create your views here.
# tasks/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import SocialTask, TaskCompletion
from .utils import verify_social_action
from django.db import transaction

@login_required
def task_list(request):
    tasks = SocialTask.objects.filter(active=True)
    
    # Apply filters
    platform = request.GET.getlist('platform')
    task_type = request.GET.getlist('type')
    
    if platform:
        tasks = tasks.filter(platform__in=platform)
    if task_type:
        tasks = tasks.filter(task_type__in=task_type)
    
    # Pagination
    paginator = Paginator(tasks, 12)
    page = request.GET.get('page')
    tasks = paginator.get_page(page)
    
    context = {
        'tasks': tasks,
        'platforms': SocialTask.PLATFORMS,
        'task_types': SocialTask.TASK_TYPES,
        'selected_platforms': platform,
        'selected_types': task_type,
    }
    
    return render(request, 'tasks/task_list.html', context)

@login_required
@require_POST
def verify_task(request, task_id):
    try:
        task = SocialTask.objects.get(id=task_id, active=True)
        
        # Verify the social action
        if verify_social_action(request.user, task):
            with transaction.atomic():
                # Update user points
                profile = request.user.profile
                profile.points += task.points_reward
                profile.save()
                
                # Create task completion record
                TaskCompletion.objects.create(
                    user=request.user,
                    task=task
                )
                
                return JsonResponse({
                    'success': True,
                    'points': profile.points
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Task verification failed. Please try again.'
            })
            
    except SocialTask.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Task not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })