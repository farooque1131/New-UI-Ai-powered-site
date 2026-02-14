from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('home/',views.home, name='home'),
    path('about/',views.about, name='about'),
    path('post-creation/',views.post_creation, name='post-creation'),
    path('edit-post/<slug>', views.edit_post, name='edit-post'),
    path('all-blogs/',views.all_blogs,name='all-blogs'),
    path('posts/<slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('authors/',views.authors, name='authors'),
    path('post/<slug>',views.post_detail, name='post-detail'),
    path('like-post/<int:id>/', views.like_post, name='like_post'),
    path('login/',views.login_user,name='login'),
    path('profile/',views.profile,name='profile'),
    path('profile/edit',views.profile_edit,name="profile_edit"),
    path('register/',views.register,name='register'),
    path("logout/", views.logout_view, name="logout"),
     # Forgot password
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='acc-end/password_reset_form.html'
         ),
         name='password_reset'),

    # Email sent
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='acc-end/password_reset_done.html'
         ),
         name='password_reset_done'),

    # Link from email
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='acc-end/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    # Password updated
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='acc-end/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
