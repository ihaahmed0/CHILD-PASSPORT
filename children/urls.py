from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
    # Children CRUD
    path('', views.children_list, name='children-list'),
    path('add/', views.add_child, name='add-child'),
    path('<str:code>/', views.child_detail, name='child-detail'),
    path('<str:code>/assessments/', views.child_assessments, name='child-assessments'),
    
    # Assessments
    path('assessments/<int:id>/update/', views.update_assessment, name='update-assessment'),
    path('assessments/categories/', views.assessment_categories, name='assessment-categories'),
    path('<str:code>/upload-photo/', views.upload_child_photo, name='upload-child-photo'),
]