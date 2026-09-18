from django.contrib import admin
from django.utils.html import format_html
from .models import Member, Family, Child, PrayerRequest, Talent


class ChildInline(admin.TabularInline):
    model = Child
    extra = 0
    max_num = 7


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('member', 'spouse_name', 'wedding_anniversary')
    search_fields = ('member__first_name', 'member__last_name', 'spouse_name')
    inlines = [ChildInline]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'photo_preview',
        'member_id',
        'full_name',
        'gender',
        'organ',
        'age_display',
        'phone',
        'is_active',
        
    )
    @admin.display(description='Photo')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #1565C0;" />',
                obj.photo.url
            )
        initial = obj.first_name[0].upper() if obj.first_name else '?'
        return format_html(
            '<div style="width: 50px; height: 50px; border-radius: 50%; background: #1565C0; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px;">{}</div>',
            initial
        )
    @admin.display(description='Current Photo')
    def photo_display(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 250px; max-width: 250px; border-radius: 10px; border: 3px solid #1565C0;" />',
                obj.photo.url
            )
        return format_html(
            '<em style="color: #999;">{}</em>',
            'No photo uploaded yet'
        )
    list_filter = ('gender', 'organ', 'is_baptized', 'is_active', 'marital_status')
    search_fields = ('member_id', 'first_name', 'last_name', 'phone', 'email')
    ordering = ('last_name', 'first_name')
    list_per_page = 25
    readonly_fields = ('member_id', 'photo_display', 'created_at', 'updated_at')
    fieldsets = (
        ('Member ID', {
            'fields': ('member_id',)
        }),
        ('Photo', {
            'fields': ('photo_display', 'photo'),
            'description': 'Upload a clear passport-size or 4x4 photo of the member.'
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address', 'occupation')
        }),
        ('Church Information', {
            'fields': ('organ', 'joined_date', 'is_baptized')
        }),
        ('Pastoral Care', {
            'fields': ('prayer_needs', 'notes'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at'),
        }),
    )

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />',
                obj.photo.url
            )
        return '—'

    @admin.display(description='Full Name', ordering='last_name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description='Age')
    def age_display(self, obj):
        age = obj.age()
        return age if age is not None else '—'


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'gender', 'age_display')
    list_filter = ('gender',)
    search_fields = ('name', 'family__member__first_name', 'family__member__last_name')

    @admin.display(description='Age')
    def age_display(self, obj):
        age = obj.age()
        return age if age is not None else '—'


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ('member', 'short_request', 'status', 'date_submitted', 'date_answered')
    list_filter = ('status', 'date_submitted')
    search_fields = ('member__first_name', 'member__last_name', 'request')
    ordering = ('-date_submitted',)
    date_hierarchy = 'date_submitted'
    readonly_fields = ('date_submitted',)

    fieldsets = (
        ('Request', {
            'fields': ('member', 'request')
        }),
        ('Status', {
            'fields': ('status', 'date_submitted', 'date_answered')
        }),
        ('Follow-up', {
            'fields': ('follow_up_notes',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Request')
    def short_request(self, obj):
        return obj.request[:60] + ('...' if len(obj.request) > 60 else '')


@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ('member', 'name', 'category', 'skill_level', 'is_available_for_ministry')
    list_filter = ('category', 'skill_level', 'is_available_for_ministry')
    search_fields = ('member__first_name', 'member__last_name', 'name', 'notes')
    ordering = ('member__last_name', 'name')
    list_per_page = 30

    fieldsets = (
        ('Talent Information', {
            'fields': ('member', 'name', 'category', 'skill_level')
        }),
        ('Ministry Availability', {
            'fields': ('is_available_for_ministry', 'notes')
        }),
    )
    