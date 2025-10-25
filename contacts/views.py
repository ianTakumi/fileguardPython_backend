from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer

    # CREATE
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # status defaults to "pending"
        return Response({
            "message": "Inquiry submitted successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # READ (ALL)
    def list(self, request, *args, **kwargs):
        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response({
            "message": "All inquiries retrieved successfully!",
            "data": serializer.data
        })

    # READ (SINGLE)
    def retrieve(self, request, *args, **kwargs):
        contact = self.get_object()
        serializer = self.get_serializer(contact)
        return Response({
            "message": "Inquiry details retrieved successfully!",
            "data": serializer.data
        })

    # UPDATE (Admin can update status here)
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Inquiry updated successfully!",
            "data": serializer.data
        })

    # DELETE
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "message": "Inquiry deleted successfully!"
        }, status=status.HTTP_204_NO_CONTENT)
