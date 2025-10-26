from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
import jwt
from .models import Contact
from .serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer

    # Helper function to validate admin token
    def _check_admin_auth(self, request):
        """Validate Bearer token and ensure user role is admin."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"message": "Authorization header missing."},
                            status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return Response({"message": "Invalid token."},
                            status=status.HTTP_401_UNAUTHORIZED)

        role = payload.get("user_metadata", {}).get("role") or payload.get("role")
        if role != "admin":
            return Response({"message": "Forbidden. Admins only."},
                            status=status.HTTP_403_FORBIDDEN)

        return None  # means valid admin

    # CREATE (anyone can submit)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # default status = "pending"
        return Response({
            "message": "Inquiry submitted successfully!",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    # READ (ALL) — Admin only
    def list(self, request, *args, **kwargs):
        auth_error = self._check_admin_auth(request)
        if auth_error:
            return auth_error

        contacts = self.get_queryset()
        serializer = self.get_serializer(contacts, many=True)
        return Response({
            "message": "All inquiries retrieved successfully!",
            "data": serializer.data
        })

    # READ (SINGLE) — public (optional: make admin-only if needed)
    def retrieve(self, request, *args, **kwargs):
        contact = self.get_object()
        serializer = self.get_serializer(contact)
        return Response({
            "message": "Inquiry details retrieved successfully!",
            "data": serializer.data
        })

    # UPDATE — Admin only
    def update(self, request, *args, **kwargs):
        auth_error = self._check_admin_auth(request)
        if auth_error:
            return auth_error

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Inquiry updated successfully!",
            "data": serializer.data
        })

    # DELETE — Admin only (optional)
    def destroy(self, request, *args, **kwargs):
        auth_error = self._check_admin_auth(request)
        if auth_error:
            return auth_error

        instance = self.get_object()
        instance.delete()
        return Response({
            "message": "Inquiry deleted successfully!"
        }, status=status.HTTP_204_NO_CONTENT)

    # COUNT — Admin only
    @action(detail=False, methods=["get"], url_path="count")
    def count_contacts(self, request):
        auth_error = self._check_admin_auth(request)
        if auth_error:
            return auth_error

        count = self.get_queryset().count()
        return Response({
            "message": "Total number of inquiries retrieved successfully!",
            "count": count
        }, status=status.HTTP_200_OK)
