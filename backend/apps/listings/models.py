"""Marketplace listings, categories and buyer applications."""

from django.db import models
from django.utils.text import slugify

from apps.core.validators import validate_uploaded_image


class Category(models.Model):
    """A coarse marketplace taxonomy, e.g. 'Tutoring' or 'Design'."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ListingModerationStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending approval'
    PUBLISHED = 'published', 'Published'
    REJECTED = 'rejected', 'Rejected'
    SUSPENDED = 'suspended', 'Suspended'
    ARCHIVED = 'archived', 'Archived'


class Listing(models.Model):
    """A service a student offers for sale, e.g. a Python tutoring package."""

    provider = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='listings'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listings',
    )
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=130, unique=True, blank=True)
    description = models.TextField(max_length=2000, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    delivery_time_days = models.PositiveSmallIntegerField(null=True, blank=True)
    is_remote = models.BooleanField(default=True)
    location = models.CharField(max_length=120, blank=True)
    skills = models.ManyToManyField(
        'profiles.Skill', related_name='listings', blank=True
    )
    cover_image = models.ImageField(
        upload_to='listings/',
        blank=True,
        null=True,
        validators=[validate_uploaded_image],
    )
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    moderation_status = models.CharField(
        max_length=12,
        choices=ListingModerationStatus.choices,
        default=ListingModerationStatus.PUBLISHED,
        help_text='Lifecycle state tracked by the moderation workflow.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['moderation_status']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:90] or 'listing'
            slug, counter = base, 2
            while Listing.objects.filter(slug=slug).exists():
                slug, counter = f'{base}-{counter}', counter + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def archive(self):
        """Soft-delete: keep the row for order history, hide from the market."""
        self.is_active = False
        self.is_archived = True
        self.save(update_fields=['is_active', 'is_archived', 'updated_at'])

    def __str__(self):
        return self.title

    @property
    def provider_username(self) -> str:
        return self.provider.user.username


class Application(models.Model):
    """A student's request to book a listing's service."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        WITHDRAWN = 'withdrawn', 'Withdrawn'

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='applications'
    )
    applicant = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='applications'
    )
    message = models.TextField(max_length=500, blank=True)
    proposed_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'applicant'],
                condition=models.Q(status='pending'),
                name='unique_pending_application',
            )
        ]

    def __str__(self):
        return f'{self.applicant.user.username} -> {self.listing.title}'
