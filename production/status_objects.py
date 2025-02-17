from django.core.exceptions import ImproperlyConfigured


class BaseStatus:
    STATUS_CHOICES: list[tuple[str, str]] = []

    def get_status(self) -> str:
        status = getattr(self, "status", None)
        if status and isinstance(status, str):
            return status
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} should have"
            f" an attribute <status>!"
        )

class PrintStatusMixin(BaseStatus):
    READY_TO_PRINT = "ready_to_print"
    IN_PROGRESS = "in_progress"
    PROBLEM = "problem"
    DONE = "done"

    STATUS_CHOICES = [
        (READY_TO_PRINT, "Ready to Print"),
        (IN_PROGRESS, "In Progress"),
        (PROBLEM, "Problem"),
        (DONE, "Done"),
    ]

    @property
    def is_editable(self):
        return self.get_status() in [
            self.READY_TO_PRINT,
            self.PROBLEM,
        ]

    @property
    def is_printable(self):
        return self.get_status() == self.READY_TO_PRINT


    @property
    def is_deletable(self) -> bool:
        return self.is_editable

    @property
    def is_done(self) -> bool:
        return self.get_status() == self.DONE



class PrinterStatusMixin(BaseStatus):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (MAINTENANCE, "Maintenance"),
    ]

    @property
    def is_active(self):
        return self.get_status() == self.ACTIVE

    @property
    def is_maintenance(self):
        return self.get_status() == self.MAINTENANCE