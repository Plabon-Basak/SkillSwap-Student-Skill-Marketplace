"""Serializers for student profiles.

Reading and writing are split: the write serializer accepts profile fields and
proxies name fields to the user account; read serializers are split into a
public and an owner-only variant so sensitive data is never exposed publicly.
"""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.profiles.models import Profile, Skill

MAX_SKILLS = 20


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug']


class ProfilePublicSerializer(serializers.Serializer):
    """Public view of a profile; deliberately excludes contact data."""

    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    display_name = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True)
    university = serializers.CharField(read_only=True)
    department = serializers.CharField(read_only=True)
    is_student = serializers.BooleanField(read_only=True)
    bio = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    experience_years = serializers.IntegerField(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    is_verified_student = serializers.BooleanField(read_only=True)
    member_since = serializers.DateTimeField(source='user.date_joined', read_only=True)
    rating_average = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_rating_average(self, profile):
        value = getattr(profile, 'rating_average', None)
        if value is None:
            return None
        return float(round(value, 2))

    @extend_schema_field(serializers.IntegerField())
    def get_rating_count(self, profile):
        value = getattr(profile, 'rating_count', None)
        if value is None:
            return 0
        return int(value)


class ProfileSelfSerializer(ProfilePublicSerializer):
    """Full view of one's own profile, including private account data."""

    email = serializers.EmailField(source='user.email', read_only=True)
    email_verified = serializers.BooleanField(
        source='user.email_verified', read_only=True
    )
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_searchable = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ProfileWriteSerializer(serializers.Serializer):
    """Create/update payload for the authenticated user's own profile."""

    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    avatar = serializers.ImageField(required=False, allow_null=True)
    university = serializers.CharField(required=False, allow_blank=True, max_length=150)
    department = serializers.CharField(required=False, allow_blank=True, max_length=150)
    is_student = serializers.BooleanField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
    location = serializers.CharField(required=False, allow_blank=True, max_length=120)
    experience_years = serializers.IntegerField(
        required=False, min_value=0, max_value=50
    )
    skills = serializers.ListField(
        child=serializers.CharField(max_length=80),
        required=False,
        max_length=MAX_SKILLS,
    )
    is_searchable = serializers.BooleanField(required=False)
    # Only staff may bless users; enforced in the view.
    is_verified_student = serializers.BooleanField(required=False, write_only=True)

    def validate_skills(self, names: list[str]) -> list[Skill]:
        cleaned: list[Skill] = []
        seen: set[str] = set()
        for raw in names:
            name = raw.strip()
            if not name:
                continue
            if name.lower() in seen:
                continue
            seen.add(name.lower())
            skill, _ = Skill.objects.get_or_create(name=name)
            cleaned.append(skill)
        return cleaned

    def _apply_to_user(self, user, validated: dict) -> None:
        for field in ('first_name', 'last_name'):
            if field in validated:
                setattr(user, field, validated[field])
        if 'first_name' in validated or 'last_name' in validated:
            user.save(update_fields=['first_name', 'last_name'])

    def _apply_to_profile(self, profile: Profile, validated: dict) -> None:
        simple_fields = [
            'avatar',
            'university',
            'department',
            'is_student',
            'bio',
            'location',
            'experience_years',
            'is_searchable',
            'is_verified_student',
        ]
        for field in simple_fields:
            if field in validated:
                setattr(profile, field, validated[field])
        if 'skills' in validated:
            profile.skills.set(validated['skills'])
        profile.save()

    def create_profile(self, user) -> Profile:
        validated = self.validated_data
        profile = Profile.objects.create(user=user)
        self._apply_to_user(user, validated)
        self._apply_to_profile(profile, validated)
        profile.refresh_from_db()
        return profile

    def update_profile(self, profile: Profile) -> Profile:
        validated = self.validated_data
        self._apply_to_user(profile.user, validated)
        self._apply_to_profile(profile, validated)
        profile.refresh_from_db()
        return profile
