from tests.test_items import TestItems


class TestModels(TestItems):

    def test_workplace_str(self) -> None:
        self.assertEqual(
            str(self.workplace1),
            f"{self.workplace1.name}"
        )


    def test_worker_str(self) -> None:
        self.assertEqual(
            str(self.regular_user),
            f"{self.regular_user.username}"
        )


    def test_material_str(self) -> None:
        self.assertEqual(
            str(self.material1),
            f"{self.material1.name}"
        )

    def test_printer_str(self) -> None:
        self.assertEqual(
            str(self.printer1),
            f"{self.printer1.name} {self.printer1.model}"
        )

    def test_print_queue_str(self) -> None:
        self.assertEqual(
            str(self.queue_m1),
            f"#{self.queue_m1.id}"
        )

    def test_order_str(self) -> None:
        self.assertEqual(
            str(self.order1_m1),
            f"#{self.order1_m1.code} | "
            f"Material: {self.order1_m1.material} | "
            f"Tiles: {self.order1_m1.tiles_count} | "
            f"m²: {self.order1_m1.square_meters}"
        )