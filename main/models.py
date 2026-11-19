from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    ROLE_CHOICES = [('regularUser', 'Regular user'), ('moderator', 'Moderator'), ('admin', 'Admin')]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regularUser')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return f'{self.user.email} ({self.role})'

    @staticmethod
    def validate_email_for_role(email, role='regularUser'):
        if not email or not email.strip():
            raise ValidationError({'email': 'Email is required.'})
        validate_email(email)
        domain = email.rsplit('@', 1)[-1].lower()
        if role == 'regularUser' and domain not in {'sdu.edu.kz', 'stu.sdu.edu.kz'}:
            raise ValidationError({'email': 'Regular accounts require an SDU email domain.'})


class Item(models.Model):
    """
    Swap Item resource for UniSwap SDU platform.
    Allows students to list items, books, gadgets, or study materials for exchange.
    """
    CATEGORY_CHOICES = [
        ('books', 'Books & Notes'),
        ('electronics', 'Electronics & Gadgets'),
        ('clothing', 'Clothing & Merch'),
        ('services', 'Tutoring & Services'),
        ('other', 'Other'),
    ]
    TYPE_CHOICES = [('Sale', 'Sale'), ('Swap', 'Swap'), ('Looking', 'Looking'), ('Free', 'Free')]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other', db_index=True)
    contact = models.CharField(max_length=150, help_text="Telegram username or SDU student email")
    listing_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Sale', db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='items/%Y/%m/', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='items')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'category_display': self.get_category_display(),
            'type': self.listing_type,
            'type_display': self.get_listing_type_display(),
            'price': str(self.price) if self.price is not None else None,
            'image_url': self.image.url if self.image else None,
            'owner_id': self.owner_id,
            'contact': self.contact,
            'is_available': self.is_available,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(self, 'updated_at') else None,
        }

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
