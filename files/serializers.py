from rest_framework import serializers
from .models import File, FileShare

class FileSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ['id', 'user_id', 'name', 'file', 'size', 'uploaded_at', 'isStarred', 'is_private', 'is_owner']
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user_id'):
            return str(obj.user_id) == request.user_id
        return True

class FileShareSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source='file.name', read_only=True)
    file_size = serializers.IntegerField(source='file.size', read_only=True)
    file_url = serializers.URLField(source='file.file', read_only=True)
    
    class Meta:
        model = FileShare
        fields = ['id', 'file', 'file_name', 'file_size', 'file_url', 'owner_id', 'shared_with_id', 'shared_at']