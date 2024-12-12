from django.test import TestCase

from production.forms import (
    WorkerCreateForm, 
    WorkerPhoneNumberForm
)


class FormsTest(TestCase):
    def setUp(self):
        self.worker_form_data = {
            "username": "new_user",
            "password1": "user12test",
            "password2": "user12test",
            "first_name": "Test first",
            "last_name": "Test last",
            "phone_number": f"+380999999999"
        }
        self.form = WorkerCreateForm(data=self.worker_form_data)
        
    @staticmethod
    def phone_number_form(number: str):
        return WorkerPhoneNumberForm(
            data={"phone_number": f"{number}"}
        )
    
    def test_worker_creation_form_is_valid(self) -> None:
        self.assertTrue(self.form.is_valid())
        self.assertEqual(self.form.cleaned_data, self.worker_form_data)


    def test_phone_number_is_valid(self) -> None:
        self.assertTrue(
            self.phone_number_form(f"+380999999999").is_valid()
        )

    def test_phone_number_not_less_than_13(self) -> None:
        self.assertFalse(self.phone_number_form("+3809").is_valid())

    def test_phone_number_not_more_than_13(self) -> None:
        self.assertFalse(
            self.phone_number_form("+3809999999999999999").is_valid()
        )

    def test_phone_number_with_invalid_characters(self) -> None:
        self.assertFalse(
            self.phone_number_form("+380ABCDEF123").is_valid()
        )