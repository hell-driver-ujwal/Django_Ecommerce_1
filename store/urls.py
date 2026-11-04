from django.urls import path
from . import views


urlpatterns =[
    path('', views.store, name ='store'),
    path('category/<slug:category_slug>/', views.store, name ='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name ='product_detail'),
    path('search/', views.search, name = 'search'),
    path("add_review/<int:product_id>/", views.add_review, name="add_review"),
    path("remove_review/<int:review_id>/", views.remove_review, name="remove_review"),
    path("edit_review/<int:review_id>/", views.edit_review, name="edit_review"),
]