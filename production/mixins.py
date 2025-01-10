from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.forms import Field, ModelChoiceField, ModelMultipleChoiceField
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic


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

    def get_absolute_url(self) -> str:
        if not self.view_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} "
                f"must define 'view_name' attribute."
            )
        return reverse(
            viewname=self.view_name,
            kwargs={
                "pk": self.pk
            }
        )


class ViewSuccessUrlMixin:
    """
    ViewSuccessUrlMixin:
    - Provides a reusable implementation of the `get_success_url` method.
    """

    def get_success_url(self):
        obj = self.get_object()
        return (
            obj.get_absolute_url()
        )



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


class FormFieldMixin:
    def get_field(self, field_name: str) -> Optional[Field]:
        """Return a form field by its name, if it exists."""
        if hasattr(self, "fields"):
            return self.fields.get(field_name, None)

    def configure_widget_attrs(self, field_name: str, attrs: dict[str, str]) -> None:
        """Update widget attributes for the given field."""
        field = self.get_field(field_name)
        if field:
            field.widget.attrs.update(attrs)
