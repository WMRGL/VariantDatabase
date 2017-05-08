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
admin.site.register(WorksheetStatusUpdate)
admin.site.register(ClassificationCode)
admin.site.register(Question)
admin.site.register(Interpretation)
admin.site.register(UserAnswer)
admin.site.register(Gene)
#admin.site.register(VariantGene)
admin.site.register(Consequence)

admin.site.register(Transcript)

admin.site.register(VariantTranscript)