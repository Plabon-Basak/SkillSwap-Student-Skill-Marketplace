"""Serializers for listings, categories and applications."""

from rest_framework import serializers

from apps.listings.models import Application, Category, Listing
from apps.profiles.models import Profile, Skill
from apps.profiles.serializers import SkillSerializer

MAX_SKILLS = 10


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id']


class ProviderSummarySerializer(serializers.Serializer):
    """The smallest public view of a listing's provider."""

    username = serializers.CharField()
    display_name = serializers.CharField()
    avatar = serializers.ImageField(allow_null=True)
    is_verified_student = serializers.BooleanField()

    def to_representation(self, profile: Profile):
        payload = {
            'username': profile.user.username,
            'display_name': profile.display_name,
            'avatar': profile.avatar,
            'is_verified_student': profile.is_verified_student,
        }
        return super().to_representation(payload)


class ListingSerializer(serializers.ModelSerializer):
    """Public representation of a listing."""

    provider = ProviderSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id',
            'slug',
            'title',
            'description',
            'provider',
            'category',
            'skills',
            'price',
            'currency',
            'delivery_time_days',
            'is_remote',
            'location',
            'cover_image',
            'is_active',
            'is_archived',
            'moderation_status',
            'created_at',
            'updated_at',
        ]


class ListingWriteSerializer(serializers.Serializer):
    """Create/update payload for a listing."""

    title = serializers.CharField(max_length=120)
    description = serializers.CharField(
        required=False, allow_blank=True, max_length=2000
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    skills = serializers.ListField(
        child=serializers.CharField(max_length=80),
        required=False,
        max_length=MAX_SKILLS,
    )
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=0)
    currency = serializers.CharField(required=False, default='USD', max_length=3)
    delivery_time_days = serializers.IntegerField(
        required=False, allow_null=True, min_value=1, max_value=730
    )
    is_remote = serializers.BooleanField(required=False, default=True)
    location = serializers.CharField(required=False, allow_blank=True, max_length=120)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_skills(self, names):
        cleaned, seen = [], set()
        for raw in names:
            name = raw.strip()
            if not name or name in seen:
                continue
            seen.add(name)
            skill, _ = Skill.objects.get_or_create(name=name)
            cleaned.append(skill)
        return cleaned

    def _apply(self, listing: Listing, validated: dict) -> Listing:
        for field in (
            'title',
            'description',
            'price',
            'currency',
            'is_remote',
            'location',
        ):
            if field in validated:
                setattr(listing, field, validated[field])
        for field in ('category', 'delivery_time_days', 'cover_image', 'is_active'):
            if field in validated:
                setattr(listing, field, validated[field])
        listing.save()
        if 'skills' in validated:
            listing.skills.set(validated['skills'])
        return listing

    def create_listing(self, provider: Profile) -> Listing:
        listing = self._apply(Listing(provider=provider), self.validated_data)
        listing.refresh_from_db()
        return listing

    def update_listing(self, listing: Listing) -> Listing:
        listing = self._apply(listing, self.validated_data)
        listing.refresh_from_db()
        return listing


class ListingSummarySerializer(serializers.ModelSerializer):
    """Compact listing shown inside an application."""

    class Meta:
        model = Listing
        fields = ['id', 'slug', 'title', 'price', 'currency', 'cover_image']


class ApplicationWriteSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True, max_length=500)
    proposed_price = serializers.DecimalField(
        required=False, allow_null=True, max_digits=8, decimal_places=2, min_value=0
    )


class ApplicationSerializer(serializers.ModelSerializer):
    """Application view; applicant data limited to the public profile."""

    listing = ListingSummarySerializer(read_only=True)
    applicant = ProviderSummarySerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'listing',
            'applicant',
            'message',
            'proposed_price',
            'status',
            'responded_at',
            'created_at',
        ]
