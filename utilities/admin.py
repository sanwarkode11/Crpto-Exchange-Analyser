import datetime

from django.contrib import admin
from django.contrib.admin import helpers
from django.forms.models import _get_foreign_key
from django.shortcuts import get_object_or_404
from import_export.admin import ImportMixin, ExportActionMixin
from simple_history import utils
from simple_history.admin import SimpleHistoryAdmin, SIMPLE_HISTORY_EDIT

from utilities.models import ProjectConfigurations


@admin.register(ProjectConfigurations)
class ProjectConfigurationsAdmin(admin.ModelAdmin):
    model = ProjectConfigurations
    fields = ('key', '_value', 'type', 'value')
    exclude = ()
    list_display = ('key', '_value', 'type')
    readonly_fields = ['value']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["key"]
        else:
            return self.readonly_fields


class ImportExportAdmin(ImportMixin, ExportActionMixin, admin.ModelAdmin):
    pass


class SimpleHistoryAdminWithInline(SimpleHistoryAdmin):
    def history_form_view(self, request, object_id, version_id, extra_context=None):
        original_opts = self.model._meta
        model = getattr(self.model, self.model._meta.simple_history_manager_attribute).model

        historical_obj = get_object_or_404(
            model, **{original_opts.pk.attname: object_id, "history_id": version_id}
        )

        historical_date = historical_obj.history_date
        adjusted_historical_date = historical_date + datetime.timedelta(seconds=10)
        print(adjusted_historical_date)

        obj = historical_obj.instance
        if "_change_history" in request.POST and SIMPLE_HISTORY_EDIT:
            history = utils.get_history_manager_for_model(obj)
            obj = history.get(pk=version_id).instance

        inline_instances = self.get_inline_instances(request, obj)
        prefixes = {}
        formset = []

        for FormSet, inline in self.get_admin_formsets_with_inline(*[request], obj):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])

            # Get historical state of the inline objects
            fk = _get_foreign_key(inline.parent_model, inline.model, fk_name=inline.fk_name)
            qs = inline.model.history.filter(**{fk.name: obj, 'history_date__lte': adjusted_historical_date,
                                                'history_type__in': ['+', '~']})

            historical_ids = []
            for inline_historical_instance in qs:
                next_record = inline_historical_instance.next_record
                if next_record is None or next_record.history_date > adjusted_historical_date:
                    historical_ids.append(inline_historical_instance.history_id)

            inline_qs = inline.model.history.filter(history_id__in=historical_ids).order_by('id')

            formset_params = {
                'instance': obj,
                'prefix': prefix,
                'queryset': inline_qs,
            }

            if request.method == 'POST':
                formset_params.update({
                    'data': request.POST.copy(),
                    'files': request.FILES,
                    'save_as_new': '_saveasnew' in request.POST
                })
            formset.append(FormSet(**formset_params))

        inline_formsets = self.get_admin_inline_formsets(request, formset, inline_instances, obj)

        extra_context_new = {'inline_admin_formsets': inline_formsets}
        extra_context_new.update(extra_context or {})

        return super(SimpleHistoryAdminWithInline, self).history_form_view(request, object_id, version_id,
                                                                           extra_context=extra_context_new)

    def get_admin_inline_formsets(self, request, formsets, inline_instances, obj=None):
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(
                inline, formset, fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets

    def get_admin_formsets_with_inline(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline
