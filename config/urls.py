from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


# Brand the admin panel
admin.site.site_header = "Zion Baptist Church — Membership System"
admin.site.site_title = "ZBC Admin"
admin.site.index_title = "Welcome to the Church Management System"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('members.urls')),  # <-- homepage
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
