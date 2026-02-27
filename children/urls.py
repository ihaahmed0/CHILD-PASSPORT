from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
     # Children CRUD
    path('', views.children_list, name='children-list'),
    path('add/', views.add_child, name='add-child'),
    path('/', views.child_detail, name='child-detail'),
    path('/assessments/', views.child_assessments, name='child-assessments'),
    path('/upload-photo/', views.upload_child_photo, name='upload-child-photo'),
    
    # Assessments
    path('assessments//', views.get_assessment_detail, name='get-assessment'),  # NEW
    path('assessments//update/', views.update_assessment, name='update-assessment'),
    path('assessments/categories/', views.assessment_categories, name='assessment-categories'),
]