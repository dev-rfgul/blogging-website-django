from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Post, Category, Comment, Like

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required
def category_filter(request, category):
    try:
        category_obj = Category.objects.get(name=category.capitalize())
        posts = Post.objects.filter(category=category_obj)
        return render(request, 'home.html', {
            'posts': posts,
            'category': category_obj.name
        })
    except Category.DoesNotExist:
        messages.error(request, f'Category "{category}" not found.')
        return redirect('home')

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_has_liked = Like.objects.filter(user=request.user, post=post).exists()
    return render(request, 'post_detail.html', {
        'post': post,
        'user_has_liked': user_has_liked
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('post_detail', post_id=post_id)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                user=request.user,
                post=post,
                content=content
            )
    return redirect('post_detail', post_id=post_id)

def search_posts(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts, 'query': query})
