"""Shared validators for user-uploaded files."""

import os

from django.core.exceptions import ValidationError

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


def validate_uploaded_image(value):
    """Reject unsafe, oversized or meaningless image uploads."""
    if value.size > MAX_UPLOAD_SIZE:
        raise ValidationError('Images must be smaller than 5 MB.')
    if getattr(value, 'content_type', None) not in ALLOWED_IMAGE_TYPES:
        raise ValidationError('Image must be a JPEG, PNG, WEBP or GIF file.')

    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError('Unsupported image extension.')
