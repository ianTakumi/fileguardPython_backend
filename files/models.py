from django.db import models
from django.contrib.auth.models import User

class File(models.Model):
    user_id = models.UUIDField()    
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='encrypted_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"
