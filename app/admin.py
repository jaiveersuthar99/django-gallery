from django.contrib import admin

from app.models import Photo, Category, Year, Video, Contact


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'thumbnail_preview')
    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        return obj.thumbnail_preview

    thumbnail_preview.short_description = 'Thumbnail Preview'
    thumbnail_preview.allow_tags = True


admin.site.register(Year)
admin.site.register(Category)
admin.site.register(Photo,PhotoAdmin)
admin.site.register(Video)
admin.site.register(Contact)

