from django.views.generic import TemplateView


class IndexView(TemplateView):
    """
    Главная страница
    """

    template_name = 'index.html'
