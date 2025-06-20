from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Team, Certificate, PrivateKey,CustomUser,UploadedFile,Website
from django.contrib import admin
from django.contrib.sessions.models import Session

from django.contrib.admin import TabularInline

class TeamInline(TabularInline):
    model = Team.members.through
    extra = 1 

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin interface for managing certificates."""
    list_display = ("id", "name", "subject", "not_after", "is_expired")
    search_fields = ("name", "subject", "issuer")

@admin.register(UploadedFile)
class UploadFileAdmin(admin.ModelAdmin):
    """Admin interface for managing uploaded files."""
    list_display = ("id", "file", "uploaded_at", "uploaded_by")
    search_fields = ("file", "uploaded_by")

@admin.register(PrivateKey)
class PrivateKeyAdmin(admin.ModelAdmin):
    """Admin interface for managing private keys."""
    list_display = ("id", "name", "uploaded_by", "certificate")
    search_fields = ("name",)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for managing teams."""
    list_display = ("id", "name")
    search_fields = ("name",)

class CustomUserAdmin(UserAdmin):
    """Admin interface for managing custom users."""
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    inlines = [TeamInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Force refresh of the 'teams' relationship
        obj.refresh_from_db()


class WebsiteAdmin(admin.ModelAdmin):
    """Admin interface for managing websites."""
    list_display = ('id', 'url', 'domain', 'certificate_name', 'display_urls')  # Add 'display_urls'
    search_fields = ('url', 'domain')
    list_filter = ('certificate',)

    # Method to display certificate's name (if available)
    def certificate_name(self, obj):
        """Display the name of the certificate associated with the website."""
        return obj.certificate.name if obj.certificate else "No Certificate"
    certificate_name.short_description = 'Certificate Name'

    # Correct way to define get_urls method
    def display_urls(self, obj):
        return obj.url  # Just return the URL field for simplicity

    display_urls.short_description = 'Website URL'  # Custom label for the 'display_urls' method

admin.site.register(Website, WebsiteAdmin)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Session)