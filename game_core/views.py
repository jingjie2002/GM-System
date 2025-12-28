from django.shortcuts import render
from .models import Project  # 导入模型


def index(request):
    # 获取所有项目数据
    projects = Project.objects.all()

    # 传递给模板
    context = {
        'projects': projects
    }
    return render(request, 'dashboard.html', context)
def tables(request):
    return render(request, 'tables.html')
def billing(request):
    return render(request, 'billing.html')
def profile(request):
    return render(request, 'profile.html')
def sign_up(request):
    return render(request, 'sign_in.html')