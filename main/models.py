from django.db import models

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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    contact = models.CharField(max_length=150, help_text="Telegram username or SDU student email")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'category_display': self.get_category_display(),
            'contact': self.contact,
            'is_available': self.is_available,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
