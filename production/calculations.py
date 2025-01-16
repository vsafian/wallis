from typing import List, Dict, Union, Any
from django.forms import BaseForm


class PrintQueueSummary:
    def __init__(
            self,
            orders=None,
            material=None
    ) -> None:
        self.orders = orders
        self.material = material

    @property
    def total_tiles(self) -> int:
        return (
            sum(order.tiles_count for order in self.orders)
            if self.orders else 0
        )

    @property
    def total_area(self) -> Union[int, float]:
        return round(
            sum(order.square_meters for order in self.orders), 2
        ) if self.orders else 0

    @property
    def winding_left(self) -> Union[int, float]:
        return (
            0 if not self.material
            else round(self.material.winding - self.total_area, 2)
        )

    @property
    def messages(self) -> List[str]:
        messages = []
        warning = "Warning: "
        if self.winding_left < 0:
            messages.append(
                warning + "You have too many orders!"
            )
        if self.total_tiles % 2 != 0:
            messages.append(
                warning + "The recommended number "
                          "of tiles must be even!"
            )
        return messages

    def as_dict(self) -> Dict[str, Union[int, float, List[str]]]:
        return {
            "total_tiles": self.total_tiles,
            "total_area": self.total_area,
            "winding_left": self.winding_left,
            "messages": self.messages,
        }

    def as_context(self):
        return {
            "summary": self.as_dict(),
        }

    def set_field(self, field_name: str, value: Any):
        if hasattr(self, field_name):
            setattr(self, field_name, value)
        else:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute {field_name}."
            )


def create_summary_context(
        form: BaseForm,
):
    """Generate Summary from form context data or initial_contex property."""
    target_fields = ["orders", "material"]
    summary = PrintQueueSummary()
    summary_context = {}
    form.is_valid()
    if hasattr(form, 'cleaned_data'):
        summary_context = form.cleaned_data
    elif hasattr(form, "initial_context"):
        summary_context = form.initial_context
    for field in target_fields:
        summary.set_field(
            field, summary_context.get(field, None)
        )
    return summary.as_context()
