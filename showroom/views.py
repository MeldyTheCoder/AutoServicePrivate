from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http.response import Http404
from django.urls import reverse_lazy
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
    'dealers': models.Dealer,
    'categories': models.ProductCategory
}

statistics_descriptions = {
    'employees': "Раздел статистики по сотрудникам.",
    'products': "Раздел статистики по товарам.",
    'dealers': "Раздел статистики по дилерам.",
    'categories': "Раздел статистики по категориям товаров."
}

statistics_models_forms = {
    'employees': forms.EmployeeForm,
    'products': forms.ProductForm,
    'dealers': forms.DealerForm,
    'categories': forms.ProductCategoryForm
}

statistics_models_tables = {
    'employees': forms.EmployeeTable,
    'products': forms.ProductTable,
    'dealers': forms.DealerTable,
    'categories': forms.ProductCategoryTable
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
    _model = None

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

        self._model = statistics_models.get(self._model_name)
        if not self._model:
            raise Http404

        object_slug = self.kwargs.get('object_slug')
        if not object_slug:
            raise Http404

        model_object = self._model.objects.get(slug=object_slug, showroom=self._showroom)
        return model_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_object = self.get_object()

        context['object'] = model_object
        context['statistics'] = model_object.statistics()
        context['model'] = self._model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        return context


class StatisticsListView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    ListView
):
    template_name = 'showroom/section_list.html'
    _model_name = None
    _showroom = None
    _model = None
    paginate_by = 20

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

        self._model = statistics_models.get(self._model_name)
        if not self._model:
            raise Http404

        return self._model.objects.filter(showroom=self._showroom)

    def get_table(self, queryset):
        table_class = statistics_models_tables.get(self._model_name)
        table = table_class(data=queryset)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context['queryset'] = queryset
        context['statistics'] = queryset.statistics(verbose_names=True)
        context['model'] = self._model
        context['model_short'] = self._model_name
        context['showroom'] = self._showroom
        context['table'] = self.get_table(queryset)
        return context


class StatisticsListStatView(StatisticsListView):
    template_name = 'showroom/section_statistics.html'


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


class ShowroomDetailView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TitleContextMixin,
    DetailView,
):

    model = models.Showroom
    template_name = 'showroom/showroom_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, slug=self.kwargs.get("showroom_slug"))

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        model_object = self.get_object()

        if user.pk != model_object.owner.pk:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.model.objects.filter(pk=self.get_object().pk)

        context['statistics_models'] = statistics_models
        context['statistics'] = object.statistics(verbose_names=True)
        return context


class ShowroomDeleteView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    DeleteView
):
    """
    Страница для удаления автосалона
    """

    form_class = forms.ShowroomDeletionForm
    template_name = 'showroom/showroom_delete.html'
    model = models.Showroom
    success_url = reverse_lazy('showroom_list')

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, slug=self.kwargs.get("showroom_slug"))


class ShowroomEditView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    UpdateView
):
    """
    Страница для редактирования автосалона
    """

    form_class = forms.ShowroomForm
    template_name = 'showroom/showroom_edit.html'
    model = models.Showroom
    success_url = None

    def get_object(self, queryset=None):
        model_object = get_object_or_404(self.model, slug=self.kwargs.get("showroom_slug"))
        self.success_url = reverse_lazy('showroom_detail', kwargs={'showroom_slug': model_object.slug})
        return model_object


class ShowroomCreateView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    CreateView
):
    """
    Страница для создания автосалона
    """

    form_class = forms.ShowroomForm
    template_name = 'showroom/showroom_add.html'
    model = models.Showroom
    success_url = reverse_lazy('showroom_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ShowroomListView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    RedirectView
):

    """
    Страница для просмотра всех автосалонов пользователя
    """

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        showrooms = user.showrooms.all()

        if not showrooms:
            return reverse_lazy('showroom_empty')

        showroom = showrooms.first()
        return reverse_lazy('showroom_detail', kwargs={'showroom_slug': showroom.slug})


class ShowroomEmptyView(
    LoginRequiredMixin,
    EmailVerifiedMixin,
    TemplateView
):
    """
    Страница для отображения автосалонов, на случай, если
    Пользователь их еще не добавил
    """

    template_name = 'showroom/showroom_empty.html'

