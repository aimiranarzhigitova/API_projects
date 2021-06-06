from django.contrib import admin

from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_display_links = ("name",)


admin.site.register(Statistics)
admin.site.register(Voice)
admin.site.register(MadeIn)
admin.site.register(Review)
admin.site.register(Customer)
admin.site.register(Vaccine)
