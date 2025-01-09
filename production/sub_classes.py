from typing import List, Dict, Union


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
                f"{warning}You have too many orders!"
            )
        if self.total_tiles % 2 != 0:
            messages.append(
                f"{warning}The recommended number of tiles must be even!"
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

    def set_orders(self, orders) -> None:
        self.orders = orders

    def set_material(self, material) -> None:
        self.material = material


def create_summary_context(
        form,
    ):
    """Generate Summary from form context data."""
    summary = PrintQueueSummary()
    form.is_valid()
    if hasattr(form, 'cleaned_data'):
        cleaned_data = form.cleaned_data
        summary.set_orders(
            cleaned_data.get('orders', None))
        summary.set_material(
            cleaned_data.get('material', None))
    return summary.as_context()
