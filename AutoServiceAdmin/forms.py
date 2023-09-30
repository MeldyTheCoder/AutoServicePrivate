from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.views.generic.edit import FormMixin


class CrispyForm(FormMixin):
    """
    Модель формы для ее автоматической верстки в bootstrap
    """

    submit_field = None

    @property
    def helper(self):
        helper = FormHelper()
        helper.field_class = 'mb-3 rounded'
        helper.form_class = 'form-control'
        helper.form_group_wrapper_class = 'mb-3'

        if self.submit_field:
            helper.add_input(
                Submit(
                    'submit',
                    self.submit_field,
                    css_class='btn rounded'
                )
            )
        return helper

