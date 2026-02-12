from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50,blank=True,null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)
    banner = models.ImageField(upload_to="banners/", blank=True, null=True)

    def __str__(self):
        return self.user.email

class Tag(models.Model):
    name = models.CharField(max_length=50) 
    def __str__(self):
        # show the title on the admin panel
        return self.name
    
class Post (models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,related_name="posts"
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = CKEditor5Field('Content', config_name='default')
    tag = models.ManyToManyField(Tag, blank=False)
    summary = models.TextField(blank=True, null=True)
    post_image = models.ImageField(upload_to='post_media/')
    published_date = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)  # NEW
    reaction = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_likes', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

# str function is used to show the name of the objects instead of id
    def __str__(self):
        # show the title on the admin panel
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # The 'self' allows a comment to point to another comment
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.post.slug