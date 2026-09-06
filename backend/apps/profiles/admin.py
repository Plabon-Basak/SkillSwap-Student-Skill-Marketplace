from django.contrib import admin

from apps.profiles.models import Profile, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'university',
        'department',
        'is_searchable',
        'is_verified_student',
        'created_at',
    )
    search_fields = ('user__username', 'user__email', 'university', 'bio')
    list_filter = ('is_searchable', 'is_verified_student', 'university')
    filter_horizontal = ('skills',)
