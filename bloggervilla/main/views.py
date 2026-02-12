from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from accountscore.forms import RegisterForm, LoginForm
from .models import Profile, Post, Comment, Tag
from .forms import ProfileForm, PostForm
from .utils import unauthorized_user, is_abusive, generate_summary
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.db.models import Count
# Create your views here.
User = get_user_model
def home(request):
    posts = Post.objects.all().order_by("-published_date")[:6]

    return render(request, 'front-end/home.html',{'posts':posts})

def about(request):
    return render(request, 'front-end/about.html')

def all_blogs(request):
    posts = Post.objects.all().order_by('-published_date')
    
    all_tags = Tag.objects.all()
    all_authors = Profile.objects.all()


    search_query = request.GET.get('search', '')
    tag_filter = request.GET.get('tag', '')
    author_filter = request.GET.get('author', '')

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        ).distinct()

    if tag_filter:
        posts = posts.filter(tag__name=tag_filter)

    if author_filter:
   
        posts = posts.filter(user_id=author_filter)

   
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    context = {
        'tag_filter': tag_filter,
        'author_filter': author_filter,
        'all_tags': all_tags,
        'all_authors': all_authors,
        'page_obj': page_obj, 
        'search': search_query # Using the single search variable
    }
    return render(request, 'front-end/all-blogs.html', context)

@login_required
def post_creation(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Post is Created Successfully!")
            redirect('all-blogs')
        else:
            messages.error(request, "Please fill all the fields correctly!")
    else:
        form = PostForm()

    return render(request, "front-end/post-creation.html", {'form':form})

def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, user=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post Updated Successfully!")
            return redirect('profile')
    
    else:
        form = PostForm(instance=post)
    
    return render(request, "front-end/post-creation.html", {'form':form, 'post':post})

def post_detail(request, slug):
    blog_content = get_object_or_404(Post, slug=slug)
    if not blog_content.summary:
        clean_text = strip_tags(blog_content.description)
        blog_content.summary = generate_summary(clean_text)
        blog_content.save(update_fields=['summary'])
    summary = blog_content.summary

    top_comments = blog_content.comments.filter(parent__isnull=True)
    profile = blog_content.user.profile
    
    context = {'blog_content':blog_content,
               'profile':profile,
               'top_comments':top_comments,
               'summary':summary}
    return render(request, 'front-end/post-detail.html',context)
@login_required
def like_post(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    post = get_object_or_404(Post, id=id)
    # Check if user liked it
    if post.reaction.filter(id=request.user.id).exists():
        post.reaction.remove(request.user)
        liked = False
    else:
        post.reaction.add(request.user)
        liked = True
    
    return JsonResponse({'liked': liked, 'total_likes': post.reaction.count()})

@login_required
def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id') # Used for nested replies
        
        parent_obj = None
        if parent_id:
            parent_obj = Comment.objects.get(id=parent_id)

        if not content:
            messages.error(request, "Please Write something!")
            return redirect('post-detail', slug=slug)
        if is_abusive(content):
            messages.error(request, "Your comment contains abusive language.")
            return redirect(request.path)
        messages.success(request, "Comment posted successfully.")
        Comment.objects.create(
            post=post,
            user=request.user,
            content=content,
            parent=parent_obj
        )
    return redirect('post-detail', slug=slug)

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Security check: only allow the author to delete
    if comment.user == request.user:
        slug = comment.post.slug
        comment.delete()
        return redirect('post-detail', slug=slug)
    return redirect('home') # Or wherever you want to send unauthorized users

def authors(request):
    # We annotate each profile with the total count of likes across all their posts
    authors = Profile.objects.annotate(
        total_likes=Count('user__posts__reaction')
    ).select_related('user')
    print(authors)
    return render(request, 'front-end/authors.html',{'authors':authors})

@unauthorized_user
def login_user(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"]
        )
        if user:
            login(request, user)
            messages.success(request, "Login Successful!")
            return redirect("home")
        else:
            messages.error(request,"Worng Credintials!")
    # return render(request, "accounts/login.html")
    return render(request, 'acc-end/login.html', {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request,"Your Succeussfully logged out!")
    return redirect("login")

def profile(request, username=None):
    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileForm(instance=profile)  
    if username:
        user_obj = get_object_or_404( User, username=username )
        is_owner = (user_obj == request.user)
    else:
        user_obj = request.user
        is_owner = True
    profile = get_object_or_404(Profile, user=user_obj)
    post_list = Post.objects.filter(user=user_obj).order_by('-published_date')
    total_post = post_list.count()
    total_comment = Comment.objects.filter(post__user=user_obj).count()
    total_reaction = Post.objects.filter(user=user_obj).aggregate(
    total=Count('reaction'))['total'] or 0
    paginator = Paginator(post_list,6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = { 'is_owner':is_owner,
                'user_obj':user_obj,
                'profile':profile,
                'form':form,
                'post_list':post_list,
                'total_post':total_post,
                'page_obj':page_obj,
                'total_comment':total_comment,
                'total_reaction':total_reaction }    

    return render(request, 'acc-end/profile.html',context)

@login_required
def profile_edit(request):
    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileForm(instance=profile)  
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update-banner":
            profile.banner = request.FILES.get("img")
            profile.save()
            messages.success(request, "Banner is Updated!")
            return redirect('profile')
        elif action == "update-avatar":
            profile.avatar = request.FILES.get("img")
            profile.save()
            messages.success(request, "Avatar is Updated!")
            return redirect('profile')
        elif action == "update_profile":
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated")
                return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'acc-end/profile-edit.html', {'form':form})
     

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account is Created Successfully!")
        return redirect("login")
    else:
        messages.error(request, "Somethin Went Worng!")
    return render(request, 'acc-end/register.html',{"form": form})