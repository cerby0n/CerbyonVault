from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.shortcuts import get_object_or_404
from certs.models import Certificate, Website
from certs.serializers import WebsiteSerializer
from django.db.models import Q


class CertificateWebsiteListCreateView(ListCreateAPIView):
    """
    GET  /api/certificates/{cert_id}/websites/  → list
    POST /api/certificates/{cert_id}/websites/  → create
    """
    serializer_class   = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # only fetch websites belonging to this certificate
        return Website.objects.filter(certificate_id=self.kwargs['cert_id'])

    def perform_create(self, serializer):
        # attach new Website to the parent Certificate
        cert = get_object_or_404(Certificate, pk=self.kwargs['cert_id'])
        # optional: check certificate.access_teams here…
        serializer.save(certificate=cert)

class WebsiteDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET /api/websites/{pk}/     → retrieve one
    PUT /api/websites/{pk}/     → update
    DELETE /api/websites/{pk}/  → delete
    """
    queryset           = Website.objects.all()
    serializer_class   = WebsiteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        
        return obj
    
class WebsiteListView(generics.ListAPIView):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer

    def get_queryset(self):
        user = self.request.user
        user_teams = user.teams.all()
        # Q1: Certificate has no access_teams
        q_no_teams = Q(certificate__access_teams=None)
        # Q2: Certificate is accessible by user's teams
        q_user_teams = Q(certificate__access_teams__in=user_teams)
        return Website.objects.filter(
            q_no_teams | q_user_teams
        ).distinct()