from unittest import TestCase

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, QuerySet
from django.forms import ModelForm
from django.http import QueryDict
from django.test import RequestFactory
from django.urls import reverse

from production.forms import WorkerSearchForm
from production.mixins import (
    ViewSuccessUrlMixin,
    ListViewSearchMixin,
    InstanceCacheMixin,
    FormFieldMixin,
    FormSaveForeignMixin,
)
from production.models import Workplace, Printer, Worker
from tests.test_items import TestItems


class TestModelAbsoluteUrlMixin(TestItems):

    def test_get_pk_for_saved_instance(self):
        pk = self.regular_user.get_pk()
        self.assertEqual(pk, self.regular_user.pk)

    def test_get_pk_for_not_saved_instance(self):
        with self.assertRaises(ImproperlyConfigured) as context:
            self.not_saved_user.get_pk()

        self.assertIn(
            "Model instance",
            str(context.exception),
            "Expected exception to include reference to model instance.",
        )
        self.assertIn(
            "should be defined in the data base.",
            str(context.exception),
            "Expected exception to inform about missing database definition.",
        )

    def test_no_view_name_raises_error(self):
        self.regular_user.view_name = ""
        with self.assertRaises(ImproperlyConfigured):
            self.regular_user.get_absolute_url()

    def test_get_absolute_url(self):
        url = self.regular_user.get_absolute_url()
        expected_url = reverse(
            "production:worker-detail", kwargs={"pk": self.regular_user.pk}
        )
        self.assertEqual(url, expected_url)


class TestViewSuccessUrlMixin(TestItems):

    def setUp(self):
        super().setUp()
        self.mixin = ViewSuccessUrlMixin()

    def test_get_success_url_with_object(self):
        self.mixin.object = self.regular_user
        expected_url = reverse(
            "production:worker-detail", kwargs={"pk": self.regular_user.pk}
        )
        self.assertEqual(expected_url, self.mixin.get_success_url())

    def test_get_success_url_without_object(self):
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.get_success_url()

    def test_get_success_url_without_view_name(self):
        self.mixin.object = self.regular_user
        delattr(get_user_model(), "view_name")
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.get_success_url()


class TestDeleteViewMixin(TestItems):

    def setUp(self):
        super().setUp()
        self.delete_url = reverse(
            "production:worker-delete", kwargs={"pk": self.regular_user.pk}
        )
        self.client.force_login(self.regular_user)

    def test_post_cancel_redirects_to_absolute_url(self):
        response = self.client.post(self.delete_url, {"cancel": "true"})
        expected_url = self.regular_user.get_absolute_url()
        self.assertRedirects(response, expected_url)

    def test_post_confirm_deletes_object(self):
        response = self.client.post(self.delete_url, {"confirm": "true"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            get_user_model().objects.filter(pk=self.regular_user.pk).exists()
        )


class TestListViewSearchMixin(TestItems):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.basic_queryset = get_user_model().objects.all()
        self.view = ListViewSearchMixin()

        self.view.object_list = self.basic_queryset
        self.view.search_form = WorkerSearchForm
        self.view.search_field = "username"
        self.view.queryset = self.basic_queryset

    def test_get_context_data_has_search_form(self):
        request = self.factory.get(f"/username={self.regular_user.username}")
        self.view.request = request
        context = self.view.get_context_data()
        self.assertIn("search_form", context)
        self.assertIsInstance(context["search_form"], WorkerSearchForm)

    def test_search_queryset_filters_correctly(self):
        username = self.regular_user.username
        request = self.factory.get(f"/?username={username}")
        expected_queryset = self.basic_queryset.filter(username__icontains=username)
        self.view.request = request
        view_queryset = self.view.get_queryset()
        self.assertQuerySetEqual(view_queryset, expected_queryset)


class TestInstanceCacheMixin(TestItems):

    class UserView(InstanceCacheMixin):
        model = get_user_model()

    def setUp(self):
        super().setUp()
        self.view = self.UserView()

    def test_cache_instance(self):
        user = self.regular_user
        self.view.kwargs = {"pk": user.pk}
        instance = self.view.cache_instance(get_user_model())
        self.assertTrue(getattr(self.view, "worker_cached"))
        self.assertEqual(instance, user)


class TestFormSaveForeignMixin(TestItems):
    class TestForm(FormSaveForeignMixin):
        printers = forms.ModelMultipleChoiceField(
            queryset=Printer.objects.all(),
            widget=forms.CheckboxSelectMultiple(),
            required=False,
        )
        related_models = [Printer]

        class Meta:
            model = Workplace
            fields = "__all__"

    def setUp(self):
        super().setUp()
        self.form_data = {"name": "Some Workplace", "printers": []}

        self.printers = [self.printer1, self.printer2]
        self.instance = self.workplace1

    def test_form_saves_related_objects_when_new_instance_created(self):
        self.form_data["printers"] = self.printers
        form = self.TestForm(self.form_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(self.printers, list(instance.printers.all()))

    def test_form_saves_related_objects_when_update_instance_data(self):
        self.form_data["printers"] = self.printers
        form = self.TestForm(instance=self.instance, data=self.form_data)
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(self.printers, list(instance.printers.all()))

    def test_form_removes_related_objects(self):
        for printer in self.printers:
            printer.workplace = self.instance
            printer.save()
        form = self.TestForm(instance=self.instance, data=self.form_data)
        instance = form.save()
        self.assertTrue(form.is_valid())
        self.assertEqual(set(instance.printers.all()), set())

    def test_missing_or_invalid_related_models_raises_exception(self):
        form = self.TestForm(data=self.form_data)
        form.related_models = []
        with self.assertRaises(ImproperlyConfigured):
            form.save()

        form.related_models = ["not_existing_model"]
        with self.assertRaises(ImproperlyConfigured):
            form.save()


class TestFormFieldMixin(TestItems):

    class TestForm(FormFieldMixin, ModelForm):
        printers = forms.ModelMultipleChoiceField(
            queryset=Printer.objects.all(),
            widget=forms.CheckboxSelectMultiple(),
            required=False,
        )

        class Meta:
            model = Workplace
            fields = "__all__"

    def setUp(self):
        super().setUp()
        self.test_field_name = "printers"
        self.form_instance = self.workplace1
        self.form = self.TestForm(instance=self.form_instance)

        self.printer1.workplace = self.form_instance
        self.printer1.save()

        self.printer2.workplace = self.workplace2
        self.printer2.save()

    def test_get_instance(self):
        self.assertEqual(self.form.get_instance(), self.form_instance)

    def test_get_field(self):
        expected_field = self.form.fields[self.test_field_name]
        self.assertEqual(self.form.get_field(self.test_field_name), expected_field)

    def test_filter_queryset_by_instance(self):
        self.form.filter_field_queryset_by_instance(self.test_field_name)

        expected_queryset = Printer.objects.filter(
            Q(workplace=self.form_instance) | Q(workplace=None)
        )

        form_queryset = self.form.fields[self.test_field_name].queryset

        self.assertQuerySetEqual(expected_queryset, form_queryset)
        self.assertNotIn(self.printer2, form_queryset)
        self.assertIn(self.printer1, form_queryset)

    def test_form_initial_context(self):
        self.form.set_initial_default_for_related_field(self.test_field_name)
        expected_context = Printer.objects.filter(workplace=self.form_instance)
        self.assertQuerySetEqual(
            expected_context, self.form.initial_context["printers"]
        )
