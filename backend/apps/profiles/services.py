"""Query helpers for student profiles."""

from django.db.models import Q

from apps.profiles.models import Profile


def get_searchable_profiles():
    """Publicly discoverable profiles with the data needed for display."""
    return (
        Profile.objects.filter(is_searchable=True)
        .select_related('user')
        .prefetch_related('skills')
        .order_by('-created_at')
    )


def search_profiles(*, query: str = '', university: str = '', skill: str = ''):
    """Filter searchable profiles by keyword, university and skill."""
    qs = get_searchable_profiles()
    if query:
        qs = qs.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(university__icontains=query)
            | Q(bio__icontains=query)
        )
    if university:
        qs = qs.filter(university__iexact=university)
    if skill:
        qs = qs.filter(skills__slug=skill.lower())
    return qs
