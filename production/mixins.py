from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.forms import Field, BaseForm
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from production.services import filter_queryset_by_instance

class DeleteViewMixin(generic.DeleteView):
    """
    DeleteViewMixin:
    - Used to handle model deletion with support for the “Cancel” and “Yes” buttons.
    - “Cancel” redirects to the model URL.
    """
    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            obj = self.get_object()
            if not hasattr(obj, 'get_absolute_url'):
                raise Http404(
                    "Object does not have an absolute URL!"
                )
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            return super().post(request, *args, **kwargs)


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
        if hasattr(self, "pk"):
            return self.pk
        raise ImproperlyConfigured(
            f"Model instance: <{self.__str__}> "
            f"should be defined in the data base."
        )

    def get_absolute_url(self) -> str:
        if not self.view_name:
            raise ImproperlyConfigured(
                f"{self.__name__} "
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
    """
    def get_success_url(self):
        if hasattr(self, "object"):
            return (
                self.object.get_absolute_url()
            )
        raise ImproperlyConfigured(
            f"View should have an object attribute."
        )


class ListViewSearchMixin(generic.ListView):
    search_form = None
    search_field: str = None
    search_queryset: QuerySet = None

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
            return self.search_queryset.filter(**search_filter)


class InstanceCacheMixin:
    model = None
    kwargs = {}

    def cache_instance(self, model):
        """
        Cache Model instance from url kwargs for avoid query
        duplication when multiple calls for instance are made.
        """
        cache_name = f"{str(self.model.__name__).lower()}_cache"
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


class FormFieldMixin:
    def get_field(self, field_name: str) -> Optional[Field]:
        """Return a form field by its name, if it exists."""
        if hasattr(self, "fields"):
            return self.fields.get(field_name, None)

    @staticmethod
    def field_queryset_exists(field: Optional[Field]) -> bool:
        return field is True and hasattr(field, "queryset")

    def configure_widget_attrs(
            self,
            field_name: str,
            attrs: dict[str, str]
    ) -> None:
        """Update widget attributes for the given field."""
        field = self.get_field(field_name)
        if field:
            field.widget.attrs.update(attrs)

    def get_instance(self):
        if hasattr(self, "instance"):
            return self.instance

    def get_initial_field(self, field_name: str) -> Field:
        if hasattr(self, "initial"):
            return self.initial.get(field_name, None)

    def set_initial_default_queryset(
            self,
            field: str,
        ) -> None:
        instance = self.get_instance()
        if hasattr(self, "initial"):
            if instance and instance.pk:
                self.initial.setdefault(
                    field, getattr(instance, field).all()
                )

    def filter_field_queryset_by_instance(
            self,
            field_name: str,
        ) -> None:
        field = self.get_field(field_name)
        if self.field_queryset_exists(field):
            instance = self.get_instance()
            field.queryset = filter_queryset_by_instance(
                queryset=field.queryset, instance=instance,
            )

    @property
    def initial_context(self):
        """Ensures that the initiated form objects
         are passed to the context
         as objects, not as ids.
        """
        fields = {}
        for field_name in self.fields:
            initial_field_data = self.get_initial_field(field_name)
            field = self.get_field(field_name)
            if isinstance(initial_field_data, QuerySet):
                fields[field_name] = self.get_initial_field(field_name)
            else:
                if hasattr(field, "queryset"):
                    if isinstance(initial_field_data, int):
                        fields[field_name] = field.queryset.get(
                            **{"id": initial_field_data}
                        )
        return fields
