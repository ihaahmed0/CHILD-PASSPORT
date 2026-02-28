from django.urls import path
from . import views

app_name = 'children'

urlpatterns = [
    # Children list and add
    path('', views.children_list, name='children-list'),
    path('add/', views.add_child, name='add-child'),
    
    # Assessment categories (no child code needed)
    path('assessments/categories/', views.assessment_categories, name='assessment-categories'),
    
    # Single assessment by ID (no child code needed)
    path('assessments/<int:id>/', views.get_assessment_detail, name='get-assessment-detail'),
    path('assessments/<int:id>/update/', views.update_assessment, name='update-assessment'),
    
    # Child-specific endpoints (child code required)
    path('<str:code>/', views.child_detail, name='child-detail'),
    path('<str:code>/assessments/', views.child_assessments, name='child-assessments'),
    path('<str:code>/upload-photo/', views.upload_child_photo, name='upload-child-photo'),
]