"""URL configuration for docqa_project project."""

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def root_view(request):
    """Root view showing the interactive API dashboard."""
    return render(request, 'index.html')


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('documents.urls')),
]
