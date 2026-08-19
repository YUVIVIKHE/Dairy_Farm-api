from django.urls import path

from field_executives.views import (
    FieldExecutiveActivateView,
    FieldExecutiveAreasView,
    FieldExecutiveDeactivateView,
    FieldExecutiveDetailView,
    FieldExecutiveListCreateView,
    FieldExecutiveResetPasswordView,
)

urlpatterns = [
    path("", FieldExecutiveListCreateView.as_view(), name="field-executive-list"),
    path("areas/", FieldExecutiveAreasView.as_view(), name="field-executive-areas"),
    path("<int:pk>/", FieldExecutiveDetailView.as_view(), name="field-executive-detail"),
    path(
        "<int:pk>/activate/",
        FieldExecutiveActivateView.as_view(),
        name="field-executive-activate",
    ),
    path(
        "<int:pk>/deactivate/",
        FieldExecutiveDeactivateView.as_view(),
        name="field-executive-deactivate",
    ),
    path(
        "<int:pk>/reset-password/",
        FieldExecutiveResetPasswordView.as_view(),
        name="field-executive-reset-password",
    ),
]
