import init_django_orm  # noqa F401

from typing import Type
from django.db import models
from django.db.models import Q, QuerySet


def get_model_plural(model: Type[models.Model] | models.Model) -> str:
    return str(model._meta.verbose_name_plural).lower()


def get_model_name(model: Type[models.Model] | models.Model) -> str:
    return str(model._meta.model_name).lower()


def foreign_case_help_text(
        field_model: Type[models.Model] | models.Model,
        foreign_model: Type[models.Model] | models.Model,
) -> str:
    return (
        "Add a new or remove an existing "
        f"{get_model_plural(field_model)} from the "
        f"{get_model_name(foreign_model)}"
    )


def filter_queryset_by_instance(queryset: QuerySet, instance: models.Model):
    """
    Filters the queryset so that it contains objects,
    that have a ForeignKey associated with instance or are None.
    """
    instance_name = get_model_name(instance)
    filter_kwargs = {
        f"{instance_name}__isnull": True
    }
    filter_related = Q(**filter_kwargs) | Q(**{instance_name: instance})
    return queryset.filter(filter_related).order_by(f"-{instance_name}")


def set_remove_foreign_by_cleaned_data_and_instance(
        model_to_update: Type[models.Model],
        cleaned_data: dict,
        instance: models.Model
) -> None:
    """
    Update foreign key relationships for a target model based on cleaned form data.

    This function processes the many-to-one or many-to-many relationships of an instance
    by checking which objects need to be added or removed. Objects that are already
    related to the instance will be detached (set to None), while new objects will
    be associated with the instance.

    """
    target_plural_name = get_model_plural(model_to_update)
    instance_name = get_model_name(instance)
    new_objects = cleaned_data.get(
        f"{target_plural_name}",
        model_to_update.objects.none()
    )
    exists_objects = getattr(
        instance, target_plural_name
    ).all()

    to_update = []

    for obj in new_objects:
        if obj in exists_objects:
            setattr(obj, instance_name, None)
        else:
            setattr(obj, instance_name, instance)
        to_update.append(obj)

    model_to_update.objects.bulk_update(
        to_update, [instance_name]
    )



