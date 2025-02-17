from typing import Optional, Type

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction, models
from django.db.models import QuerySet
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django_filters.views import FilterView

from production.services import (
    filter_queryset_by_instance,
    model_name_to_field,
    set_remove_foreign_by_cleaned_data_and_instance
)


class ModelAbsoluteUrlMixin:
    """
    ModelAbsoluteUrlMixin:
    - Provides a reusable implementation of the `get_absolute_url` method.
    - Generates an absolute URL for an object based on a predefined view name.

    Attributes:
        view_name (str): The name of the URL pattern to reverse.
                         Must be defined in the subclass.
    """
    view_name: str = ""

    def get_pk(self):
        if hasattr(self, "pk") and self.pk:
            return self.pk
        raise ImproperlyConfigured(
            f"Model instance: <{self}> "
            f"should be defined in the data base."
        )

    def get_absolute_url(self) -> str:
        if not self.view_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} "
                f"must define 'view_name' attribute."
            )
        return reverse(
            viewname=self.view_name,
            kwargs={
                "pk": self.get_pk(),
            }
        )


class ViewSuccessUrlMixin:
    """
    ViewSuccessUrlMixin:
    - Provides a reusable implementation of the `get_success_url` method.
    (!) Works only with defined view_name from ModelAbsoluteUrlMixin.
    """

    def get_success_url(self):
        if (hasattr(self, "object")
            and hasattr(self.object, "view_name")):
            return (
                self.object.get_absolute_url()
            )
        raise ImproperlyConfigured(
            f"View should have an object attribute"
            f" and defined view name."
        )


class DeleteViewMixin(generic.DeleteView):
    """
    DeleteViewMixin:
    - Used to handle model deletion with support for the “Cancel” and “Yes” buttons.
    - “Cancel” redirects to the model URL.
    """

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            instance = self.get_object()
            url = getattr(instance, "get_absolute_url", None)
            if url and callable(url):
                return HttpResponseRedirect(url())
            raise Http404(
                "Object does not have an absolute URL!"
            )
        else:
            return super().post(request, *args, **kwargs)


class ListViewSearchMixin(
    generic.ListView
):
    search_form = None
    search_field: str = None
    queryset: QuerySet = None

    def dispatch(self, request, *args, **kwargs):
        fields = ["search_form", "search_field", "queryset"]
        for field_name in fields:
            field = getattr(self, field_name, None)
            if not field:
                raise ImproperlyConfigured(
                    f"ListViewSearchMixin requires {field_name} to be defined."
                )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        field = self.request.GET.get(self.search_field, "")
        context["search_form"] = self.search_form(
            initial={self.search_field: field}
        )
        return context

    def get_queryset(self) -> QuerySet:
        form = self.search_form(self.request.GET)
        if form.is_valid():
            search_filter = {
                f"{self.search_field}__icontains":
                    form.cleaned_data[self.search_field]
            }
            return self.queryset.filter(**search_filter)
        return self.queryset

class InstanceCacheMixin:
    model = None
    kwargs = {}

    def cache_instance(self, model):
        """
        Cache Model instance from url kwargs for avoid query
        duplication when multiple calls for instance are made.
        """
        cache_name = f"{model_name_to_field(self.model)}_cached"
        if not hasattr(self, cache_name):
            setattr(
                self,
                cache_name,
                get_object_or_404(
                    model,
                    pk=self.kwargs["pk"]
                )
            )
        return getattr(self, cache_name)


class PostApproveMixin(generic.FormView):
    def post(self, request, *args, **kwargs):
        form = self.get_context_data()["form"]
        if "approve" in request.POST and form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)


class FormSaveForeignMixin(forms.ModelForm):
    """
    A mixin that ensures foreign key relations
    are properly updated on save.
    """
    related_models: list[Type[models.Model]] = []

    def _validate_related_models(self) -> None:
        """
        Ensure that related_models is correctly
        set and contains only Django model classes.
        """
        if not self.related_models:
            raise ImproperlyConfigured(
                "`related_models` should not be empty. "
                f"Define at least one model in {self.__class__.__name__}."
            )

        if not all(isinstance(model, type)
                and issubclass(model, models.Model)
                for model in self.related_models
        ):
            raise ImproperlyConfigured(
                "`related_models` should contain only Django model classes."
            )

    def save(self, commit=True):
        """
        Save the instance and update related models.
        """
        self._validate_related_models()
        instance = super().save(commit=False)
        if commit:
            with transaction.atomic():
                instance.save()
                for model in self.related_models:
                    set_remove_foreign_by_cleaned_data_and_instance(
                        model_to_update=model,
                        cleaned_data=self.cleaned_data,
                        instance=instance,
                    )
        return instance


class FormFieldMixin:
    def get_field(self, field_name: str) -> Optional[forms.Field]:
        """Return a form field by its name,
        if it exists and is instance of forms.Field."""
        if hasattr(self, "fields"):
            field = self.fields.get(field_name, None)
            if isinstance(field, forms.Field):
                return field
            raise ImproperlyConfigured(
                f"There is no {field_name} attribute in {self.__class__.__name__} fields."
            )
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} must define `fields` attribute."
        )

    def set_field_pseudo_dynamic(self, field_name: str) -> None:
        """
        Allow field to trigger form submission on change.
        (!) Use only in views with 'PostApproveMixin'
        """
        field = self.get_field(field_name)
        field.widget.attrs["onchange"] = "this.form.submit();"

    def set_form_widget_css(self, field_name: str, css_class: str) -> None:
        """Add CSS classes inside the field widget"""
        field = self.get_field(field_name)
        field.widget.attrs["class"] = css_class

    def disable_field(self, field_name: str) -> None:
        field = self.get_field(field_name)
        field.disabled = True

    def get_instance(self):
        if hasattr(self, "instance"):
            return self.instance

    def get_initial_field(self, field_name: str) -> forms.Field:
        if hasattr(self, "initial"):
            return self.initial.get(field_name, None)

    def set_initial_default_for_related_field(
            self,
            field: str,
    ) -> None:
        """
        Validate form instance and set
        initial default if field is related.
        """
        instance = self.get_instance()
        if hasattr(self, "initial"):
            if instance and instance.pk:
                relation_object = getattr(
                    instance, field
                )
                if isinstance(relation_object, models.Manager):
                    self.initial.setdefault(
                        field, relation_object.all()
                    )

    def get_field_queryset(self, field_name: str) -> QuerySet:
        field = self.get_field(field_name)
        if hasattr(field, "queryset"):
            return field.queryset
        raise ImproperlyConfigured(
            f"{field_name} should define `queryset` attribute."
        )

    def set_field_queryset(
            self,
            field_name: str,
            queryset: QuerySet
    ) -> None:
        field = self.get_field(field_name)
        if hasattr(field, "queryset"):
            setattr(field, "queryset", queryset)
        else:
            raise ImproperlyConfigured(
                f"Field `{field_name}` does not support `queryset`."
            )

    def filter_field_queryset_by_instance(
            self,
            field_name: str,
    ) -> None:
        self.set_field_queryset(
            field_name=field_name,
            queryset=filter_queryset_by_instance(
                queryset=self.get_field_queryset(field_name),
                instance=self.get_instance(),
            )
        )

    @property
    def initial_context(self):
        """
        Track of form fields by fetching initial data from it
        and, if the initial data is a query set, pass it on.
        Otherwise, if the data contains an int (id)
        convert id to object.
        (!) Object will be getting from field query set.
        """
        fields = {}
        if hasattr(self, "fields"):
            for field_name in self.fields:
                initial_field_data = self.get_initial_field(field_name)
                field = self.get_field(field_name)
                if isinstance(initial_field_data, QuerySet):
                    fields[field_name] = self.get_initial_field(field_name)
                else:
                    if hasattr(field, "queryset"):
                        if isinstance(initial_field_data, int):
                            queryset = getattr(field, "queryset")
                            fields[field_name] = queryset.get(
                                **{"id": initial_field_data}
                            )
            return fields
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} "
            f"has not fields attribute."
        )


class FilterFieldMixin(
    FormFieldMixin,
):
    def get_field(self, field_name: str) -> Optional[forms.Field]:
        if hasattr(self, "filters"):
            return self.filters[field_name].field
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} has no `filters` attribute."
        )
