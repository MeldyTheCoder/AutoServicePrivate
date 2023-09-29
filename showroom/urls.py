from django.urls import path
from . import views

urlpatterns = [
    # Ссылки по модели автосалона #
    path(
        'showroom/<slug:showroom_slug>/',
        views.ShowroomDetailView.as_view(),
        name='showroom_view'
    ),
    path(
        'showroom/<slug:showroom_slug>/delete/',
        views.ShowroomDeleteView.as_view(),
        name='showroom_delete'
    ),
    path(
        'showroom/<slug:showroom_slug>/edit/',
        views.ShowroomEditView.as_view(),
        name='showroom_edit'
    ),
    path(
        'showroom/create/',
        views.ShowroomCreateView.as_view(),
        name='showroom_create'
    ),

    path(
        'showroom/<slug:showroom_slug>/<str:model_name>/create/',
        views.StatisticsCreateView.as_view(),
        name='statistics_create'
    ),
    path(
        'showroom/<slug:showroom_slug>/<str:model_name>/<slug:object_slug>/edit/',
        views.StatisticsEditView.as_view(),
        name='statistics_edit'
    ),
    path(
        'showroom/<slug:showroom_slug>/<str:model_name>/<slug:object_slug>/delete/',
        views.StatisticsDeleteView.as_view(),
        name='statistics_delete'
    ),
    path(
        'showroom/<slug:showroom_slug>/<str:model_name>/<slug:object_slug>/',
        views.StatisticsDetailView.as_view(),
        name='statistics_detail'
    ),
    path(
        'showroom/<slug:showroom_slug>/<str:model_name>/',
        views.StatisticsListView.as_view(),
        name='statistics_list'
    )
]
