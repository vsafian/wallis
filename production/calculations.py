from typing import List, Dict, Union, Any
from django.forms import BaseForm

from .status_objects import PrintStatusMixin


class PrintQueueSummary:
    def __init__(self, orders=None, material=None) -> None:
        self.orders = orders
        self.material = material

    @property
    def total_tiles(self) -> int:
        return sum(order.tiles_count for order in self.orders) if self.orders else 0

    @property
    def total_area(self) -> Union[int, float]:
        return (
            round(sum(order.square_meters for order in self.orders), 2)
            if self.orders
            else 0
        )

    @property
    def winding_left(self) -> Union[int, float]:
        return (
            0
            if not self.material
            else round(self.material.winding - self.total_area, 2)
        )

    @property
    def messages(self) -> List[str]:
        messages = []
        warning = "Warning: "
        if self.winding_left < 0:
            messages.append(warning + "You have too many orders!")
        if self.total_tiles % 2 != 0:
            messages.append(
                warning + "The recommended number " "of tiles must be even!"
            )
        if self.orders:
            problem_orders = self.orders.filter(status=PrintStatusMixin.PROBLEM)
            if problem_orders.exists():
                messages.append(warning + "There are problem orders:")
                for order in problem_orders:
                    messages.append(f"{order};")
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

    def set_orders(self, orders: Any):
        self.orders = orders

    def set_material(self, material: Any):
        self.material = material

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
    """Generate Summary from form context data or initial_context property."""
    summary = PrintQueueSummary()
    summary_context = {}
    form.is_valid()
    if hasattr(form, "cleaned_data"):
        summary_context = form.cleaned_data
    elif hasattr(form, "initial_context"):
        summary_context = form.initial_context
    material = summary_context.get("material", None)
    orders = summary_context.get("orders", None)
    summary.set_material(material)
    summary.set_orders(orders)
    return summary.as_context()
