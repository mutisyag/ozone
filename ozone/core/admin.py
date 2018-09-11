from django.contrib import admin

# Register your models here.
from .models import (
    Meeting,
    Treaty,
    Decision,
    Region,
    Subregion,
    Party,
    PartyHistory,
    ReportingPeriod,
    Obligation,
    Annex,
    Group,
    Substance,
    Blend,
    BlendComponent,
)

# Meeting-related models
admin.site.register(Meeting)


@admin.register(Treaty)
class TreatyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Decision)

# Party-related models
admin.site.register(Region)
admin.site.register(Subregion)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'subregion')


@admin.register(PartyHistory)
class PartyHistoryAdmin(admin.ModelAdmin):
    list_display = ('party', 'year')


# Substance-related models
@admin.register(Annex)
class AnnexAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


admin.site.register(Group)


@admin.register(Substance)
class SubstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')


admin.site.register(Blend)
admin.site.register(BlendComponent)

# Reporting-related models
admin.site.register(ReportingPeriod)
admin.site.register(Obligation)
