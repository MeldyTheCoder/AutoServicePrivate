from django import template

register = template.Library()


@register.inclusion_tag('account/inclusions/profile_sidebar.html', name='profile_sidebar', takes_context=True)
def profile_sidebar(context):
    return context




