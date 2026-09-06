"""Student profiles and the taxonomies that describe their skills."""

from django.db import models
from django.utils.text import slugify

from apps.core.validators import validate_uploaded_image


class Skill(models.Model):
    """A reusable, searchable capability label (e.g. 'Python', 'Video editing')."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Kept as an alias so the committed migration (apps.profiles.models.validate_avatar)
# keeps resolving; behaviour now lives in the shared validator.
validate_avatar = validate_uploaded_image


class Profile(models.Model):
    """Marketplace-facing information about a student.

    The user account owns identity/credentials; the profile carries the
    publicly visible details sold through the marketplace. Sensitive fields
    (contact data) are never exposed by the public serializer.
    """

    user = models.OneToOneField(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[validate_avatar],
    )
    university = models.CharField(max_length=150, blank=True)
    department = models.CharField(max_length=150, blank=True)
    is_student = models.BooleanField(default=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=120, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    skills = models.ManyToManyField(Skill, related_name='profiles', blank=True)

    # Privacy control: allow the profile to be discoverable in marketplace
    # search and public listings.
    is_searchable = models.BooleanField(default=True)

    # Badge set by moderators after verifying the student claimed identity.
    is_verified_student = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['university']),
            models.Index(fields=['is_searchable', 'is_verified_student']),
        ]

    def __str__(self):
        return f'Profile for {self.user.username}'

    @property
    def display_name(self) -> str:
        name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return name or self.user.username
