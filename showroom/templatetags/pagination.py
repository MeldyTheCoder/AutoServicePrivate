from django import template
from django.http import QueryDict

register = template.Library()


@register.inclusion_tag('inclusions/pagination.html', name='pagination', takes_context=True)
def pagination(context):
    return context


@register.simple_tag(name='middle_pages')
def middle_pages(page_obj):
    pages = []
    side_pages = 3
    total_pages = page_obj.paginator.num_pages
    available_pages = [_ for _ in range(1, total_pages+1)]
    current_page = page_obj.number

    if not current_page:
        current_page = 1

    if current_page > total_pages:
        current_page = total_pages

    if current_page - side_pages - 1 <= 0:
        previous_pages_start = 0
    else:
        previous_pages_start = current_page - side_pages - 1

    if current_page < side_pages:
        next_pages_slice = slice(current_page, current_page + side_pages + (side_pages - current_page), None)
    else:
        next_pages_slice = slice(current_page, current_page + side_pages + 1, None)

    if total_pages - current_page < side_pages:
        previous_pages_slice = slice(previous_pages_start - (side_pages + current_page), current_page, None)
    else:
        previous_pages_slice = slice(previous_pages_start, current_page, None)

    pages.extend(available_pages[previous_pages_slice])
    pages.append(current_page)
    pages.extend(available_pages[next_pages_slice])

    pages = list(set(pages))
    pages.sort()
    return pages


@register.simple_tag(name='build_url')
def page_url(request, **kwargs):
    url_query = QueryDict(query_string=request.GET.urlencode(), mutable=True)
    for key, val in kwargs.items():
        if not val and url_query.get(key):
            del url_query[key]
        else:
            url_query[key] = val

    return f"{request.path}?{url_query.urlencode()}"
