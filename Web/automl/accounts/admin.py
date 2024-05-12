from django.contrib import admin
# Register your models here.
from .models import User, UserFile

admin.site.register(User)
admin.site.register(UserFile)