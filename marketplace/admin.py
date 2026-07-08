from django.contrib import admin
from .models import WorkerProfile, Review

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill', 'location', 'availability', 'is_verified', 'is_premium', 'average_rating')
    list_filter = ('skill', 'location', 'availability', 'is_verified', 'is_premium')
    search_fields = ('name', 'mobile_number', 'bio')
    actions = ['verify_workers', 'make_premium']

    def verify_workers(self, request, queryset):
        queryset.update(is_verified=True)
    verify_workers.short_description = "Mark selected workers as Verified"

    def make_premium(self, request, queryset):
        queryset.update(is_premium=True)
    make_premium.short_description = "Mark selected workers as Premium"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('worker', 'customer_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer_name', 'comment')
