from django.contrib import admin

from .models import *


admin.site.register(Project)
admin.site.register(Batch)
admin.site.register(Sample)

