import re
from django import template
from showroom.views import statistics_descriptions


register = template.Library()


@register.inclusion_tag('showroom/inclusions/showroom_list_sidebar.html', name='showroom_sidebar', takes_context=True)
def showroom_sidebar(context):
    return context


@register.inclusion_tag(
    'showroom/inclusions/statistics_model_card.html',
    name='statistics_model_card'
)
def statistics_model_card(model_short, model, showroom):
    return {
        'description': statistics_descriptions.get(model_short),
        'model_short': model_short,
        'model': model,
        'verbose_name': model._meta.verbose_name,
        'verbose_name_plural': model._meta.verbose_name_plural,
        'showroom': showroom,
    }


@register.filter(name='stat_value')
def stat_value_replace_none(object):
    if not object:
        return 0

    if object == 'None':
        return 0

    integer_separator = ','
    decimal_separator = '.'

    if not integer_separator:
        integer_separator = ' '

    if not decimal_separator:
        decimal_separator = '.'

    if integer_separator == decimal_separator:
        integer_separator = ' '
        decimal_separator = '.'

    string_value = str(object)

    if decimal_separator in string_value:
        value_parts = string_value.split(decimal_separator)
        integer = value_parts[0]
        decimal = value_parts[1].replace('0', '')

        if not decimal:
            string_value = integer
        else:
            string_value = f"{integer}.{decimal}"

    new = re.sub(r"^(-?\d+)(\d{3})", rf"\g<1>{integer_separator}\g<2>", string_value)
    if string_value == new:
        return new
    else:
        return stat_value_replace_none(new)
    return object
