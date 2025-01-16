from typing import Type
from django.db import models
from django.db.models import Q, QuerySet


def model_name_to_field(
        model: Type[models.Model] | models.Model
) -> str:
    return "_".join(
        model._meta.verbose_name.split()
    )


def model_to_related_name(model: Type[models.Model]) -> str:
    return "_".join(
        model._meta.verbose_name_plural.split()
    )


def foreign_case_help_text(
        field_name: str,
        instance_name: str,

) -> str:
    return (
        "Add a new or remove an existing "
        f"{field_name} from the "
        f"{instance_name}."
    )


def filter_queryset_by_instance(
        queryset: QuerySet,
        instance: models.Model,
):
    """
    Filters the queryset so that it contains objects,
    that have a ForeignKey associated with instance
    or instance ForeignKey are None.
    """
    instance_foreign_name = model_name_to_field(instance)
    instance_none = {
        f"{instance_foreign_name}__isnull": True
    }
    if instance.pk:
        filter_related = (
                Q(**instance_none) |
                Q(**{instance_foreign_name: instance})
        )
        return (
            queryset.filter(filter_related)
            .order_by(f"-{instance_foreign_name}")
        )
    return queryset.filter(**instance_none)


def set_remove_foreign_by_cleaned_data_and_instance(
        model_to_update: Type[models.Model],
        cleaned_data: dict[str, QuerySet[models.Model]],
        instance: models.Model
) -> None:
    """
    Update foreign key relationships for a target model based on cleaned form data.

    This function processes the many-to-one or many-to-many relationships of an instance
    by checking which objects need to be added or removed.
    If the previously connected objects
    are not in the list of new objects, they will be disconnected.
    """
    target_related_name = model_to_related_name(
        model_to_update
    )
    instance_name = model_name_to_field(instance)

    new_objects = cleaned_data.get(
        target_related_name,
        model_to_update.objects.none()
    )

    exists_objects = getattr(
        instance, target_related_name
    ).all()

    to_update = []

    for obj in exists_objects:
        if obj not in new_objects:
            setattr(obj, instance_name, None)
            to_update.append(obj)

    for obj in new_objects:
        if obj not in exists_objects:
            setattr(obj, instance_name, instance)
            to_update.append(obj)

    model_to_update.objects.bulk_update(
        to_update, [instance_name]
    )
