from django.contrib import admin

from .models import *


admin.site.register(Section)
admin.site.register(Worksheet)
admin.site.register(Sample)
admin.site.register(VariantInformation)
admin.site.register(UserSetting)
admin.site.register(Variant)

admin.site.register(VariantSample)
admin.site.register(SampleStatus)
admin.site.register(WorkSheetStatus)
admin.site.register(SampleStatusUpdate)