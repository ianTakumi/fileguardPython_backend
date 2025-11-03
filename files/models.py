from django.db import models

class File(models.Model):
    user_id = models.UUIDField()
    name = models.CharField(max_length=255)
    file = models.URLField(blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    isStarred = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} by {self.user_id}"

class FileShare(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shares')
    owner_id = models.UUIDField()
    shared_with_id = models.UUIDField()
    shared_at = models.DateTimeField(auto_now_add=True)
    # Tinanggal na ang can_edit field - download lang ang permission
    
    class Meta:
        unique_together = ['file', 'shared_with_id']
    
    def __str__(self):
        return f"{self.file.name} shared by {self.owner_id} with {self.shared_with_id}"