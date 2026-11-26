from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from .models import Item
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    def clean(self):
        email = self.data.get(self.add_prefix('username'), '').strip().lower()[:254]
        ip = self.request.META.get('REMOTE_ADDR', 'unknown')
        keys = [f'auth-attempt:email:{email}', f'auth-attempt:ip:{ip}']
        if any(cache.get(key, 0) >= limit for key, limit in zip(keys, (10, 30))):
            raise ValidationError('Too many sign-in attempts. Please try again later.')
        result = super().clean()
        if not self.get_user():
            for key in keys:
                try:
                    cache.add(key, 0, timeout=900)
                    cache.incr(key)
                except ValueError:
                    cache.set(key, 1, timeout=900)
        else:
            for key in keys:
                cache.delete(key)
        return result


def validate_sdu_email(value):
    validate_email(value)
    domain = value.rsplit('@', 1)[-1].lower()
    if domain not in {'sdu.edu.kz', 'stu.sdu.edu.kz'}:
        raise ValidationError('Use an @sdu.edu.kz or @stu.sdu.edu.kz address.')


class ManagedUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, validators=[validate_sdu_email])

    class Meta:
        model = get_user_model()
        fields = '__all__'

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        duplicates = get_user_model().objects.filter(email__iexact=email)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        data = super().clean()
        email = data.get('email')
        if email:
            email = email.strip().lower()
            data['email'] = email
            validate_sdu_email(email)
        return data


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'description', 'category', 'listing_type', 'price', 'contact', 'image')
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image must be 5 MB or smaller.')
            validate_image_file_extension(image)
            try:
                image.image.verify()
            except (OSError, ValueError):
                raise ValidationError('Upload a valid image file.')
        return image
