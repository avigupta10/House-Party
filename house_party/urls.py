from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend.urls')),
    path('', include('frontend.urls')),
    path('spotify/', include('spotify.urls')),
]
