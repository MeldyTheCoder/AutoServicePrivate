from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http.response import Http404
from django.apps import apps
from django.views.generic.base import ContextMixin
from django.views.generic import (
    UpdateView,
    TemplateView,
    CreateView,
    RedirectView,
    DetailView,
    ListView,
    DeleteView,
)

from . import models, forms
from account.mixins import EmailVerifiedMixin


statistics_models = {
    'employees': models.Employee,
    'products': models.Product,
    'sales': models.ProductSale,
    'supplies': models.ProductSupply,
    'dealers': models.Dealer,
    'categories': models.ProductCategory
}

statistics_models_forms = {
    'employees': forms.EmployeeForm,
    'products': forms.EmployeeForm,
    'sales': forms.ProductSaleForm,
    'supplies': forms.ProductSupplyForm,
    'dealers': forms.DealerForm,
    'categories': forms.ProductCategoryForm
}


class TitleContextMixin(ContextMixin):
    title = None
    text = None

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = self.get_title()
        context['text'] = self.get_text()
        return context


class StatisticsDetailView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    DetailView
):
    template_name = 'showroom/section_item_statistics.html'
    _model_name = None
    _showroom = None

    def get_object(self, queryset=None):
        showroom_slug = self.kwargs.get('showroom_slug')
        if not showroom_slug:
            raise Http404

        self._showroom = get_object_or_404(
            models.Showroom,
            slug=showroom_slug,
            owner=self.request.user
        )

        self._model_name = self.kwargs.get('model_name')
        if not self._model_name:
            raise Http404

        model = statistics_models.get(self._model_name)
        if not model:
            raise Http404

        object_slug = self.kwargs.get('object_slug')
        if not object_slug:
            raise Http404

        model_object = model.objects.get(slug=object_slug, showroom=self._showroom)
        return model_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_object = self.get_object()

        context['object'] = model_object
        context['statistics'] = model_object.statistics()
        context['model'] = model_object._meta.model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        return context


class StatisticsListView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    ListView
):
    _model_name = None
    _showroom = None

    def get_queryset(self):
        showroom_slug = self.kwargs.get('showroom_slug')
        if not showroom_slug:
            raise Http404

        self._showroom = get_object_or_404(
            models.Showroom,
            slug=showroom_slug,
            owner=self.request.user
        )

        self._model_name = self.kwargs.get('model_name')
        if not self._model_name:
            raise Http404

        model = statistics_models.get(self._model_name)
        if not model:
            raise Http404

        return model.objects.filter(showroom=self._showroom)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context['queryset'] = queryset
        context['statistics'] = queryset.statistics()
        context['model'] = queryset.model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        return context


class StatisticsEditView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    UpdateView
):
    template_name = 'showroom/section_item_edit.html'
    _model_name = None
    _showroom = None

    def get_object(self, queryset=None):
        showroom_slug = self.kwargs.get('showroom_slug')
        if not showroom_slug:
            raise Http404

        self._showroom = get_object_or_404(
            models.Showroom,
            slug=showroom_slug,
            owner=self.request.user
        )

        self._model_name = self.kwargs.get('model_name')
        if not self._model_name:
            raise Http404

        model = statistics_models.get(self._model_name)
        if not model:
            raise Http404

        self.form_class = statistics_models_forms.get(self._model_name)

        object_slug = self.kwargs.get('object_slug')
        if not object_slug:
            raise Http404

        model_object = model.objects.get(slug=object_slug, showroom=self._showroom)
        return model_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_object = self.get_object()

        context['object'] = model_object
        context['statistics'] = model_object.statistics()
        context['model'] = model_object._meta.model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        return context


class StatisticsCreateView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    CreateView
):
    template_name = 'showroom/section_item_create.html'
    _model_name = None
    _showroom = None

    def dispatch(self, request, *args, **kwargs):
        showroom_slug = self.kwargs.get('showroom_slug')
        if not showroom_slug:
            raise Http404

        self._showroom = get_object_or_404(
            models.Showroom,
            slug=showroom_slug,
            owner=self.request.user
        )

        self._model_name = self.kwargs.get('model_name')
        if not self._model_name:
            raise Http404

        model = statistics_models.get(self._model_name)
        if not model:
            raise Http404

        self.model = model
        self.form_class = statistics_models_forms.get(self._model_name)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object'] = None
        context['model'] = self.model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        return context

    def form_valid(self, form):
        form.instance.showroom = self._showroom
        return super().form_valid(form)


class StatisticsDeleteView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    DeleteView
):
    template_name = 'showroom/section_item_delete.html'
    _model_name = None

    def get_object(self, queryset=None):
        showroom_slug = self.kwargs.get('showroom_slug')
        if not showroom_slug:
            raise Http404

        showroom = get_object_or_404(
            models.Showroom,
            slug=showroom_slug,
            owner=self.request.user
        )

        self._model_name = self.kwargs.get('model_name')
        if not self._model_name:
            raise Http404

        model = statistics_models.get(self._model_name)
        if not model:
            raise Http404

        object_slug = self.kwargs.get('object_slug')
        if not object_slug:
            raise Http404

        model_object = model.objects.get(slug=object_slug, showroom=showroom)
        return model_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_object = self.get_object()

        context['object'] = model_object
        context['statistics'] = model_object.statistics()
        context['model'] = model_object._meta.model
        context['model_short'] = self._model_name
        return context


class ShowroomDetailView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    DetailView,
):

    model = models.Showroom
    template_name = 'showroom/showroom_detail.html'

    def get_object(self, queryset=None):
        return queryset.get(slug=self.kwargs.get("slug"))

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        model_object = self.get_object(self.queryset)

        if user.pk != model_object.owner.pk:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics'] = self.get_object(self.queryset).statistics()
        return context


class ShowroomDeleteView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    DeleteView
):
    """
    Страница для удаления автосалона
    """

    template_name = 'showroom/showroom_delete.html'
    model = models.Showroom


class ShowroomEditView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    UpdateView
):
    """
    Страница для редактирования автосалона
    """

    template_name = 'showroom/showroom_edit.html'
    model = models.Showroom


class ShowroomCreateView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    CreateView
):
    """
    Страница для создания автосалона
    """

    template_name = 'showroom/showroom_add.html'
    model = models.Showroom
