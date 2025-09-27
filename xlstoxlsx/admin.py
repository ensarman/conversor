from django.contrib import admin
from .models import ConversionRecord


@admin.register(ConversionRecord)
class ConversionRecordAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename',
        'converted_filename',
        'conversion_successful',
        'file_size',
        'created_at'
    ]
    list_filter = ['conversion_successful', 'created_at']
    search_fields = ['original_filename', 'converted_filename']
    readonly_fields = ['created_at', 'file_size']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['original_file', 'converted_file']
        return self.readonly_fields
