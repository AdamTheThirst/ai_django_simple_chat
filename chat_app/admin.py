from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'role', 'short_content')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)

    @staticmethod
    def short_content(obj):
        return obj.content[:80]
