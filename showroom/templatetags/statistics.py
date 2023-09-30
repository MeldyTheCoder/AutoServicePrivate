from django import template
from showroom.views import statistics_models, statistics_models_tables

register = template.Library()


@register.inclusion_tag('showroom/inclusions/sections_sidebar.html', name='statistics_sidebar', takes_context=True)
def statistics_sidebar(context, **kwargs):
    context['statistics_models_verbose_names'] = {
        model_short: model._meta.verbose_name for model_short, model in statistics_models.items()
    }

    context['statistics_models_verbose_names_plural'] = {
        model_short: model._meta.verbose_name_plural for model_short, model in statistics_models.items()
    }

    return context


@register.filter(name='verbose_name')
def verbose_name(object):
    return object._meta.verbose_name


@register.filter(name='verbose_name_plural')
def verbose_name(object):
    return object._meta.verbose_name_plural


