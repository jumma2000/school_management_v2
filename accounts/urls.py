from django.urls import path


urlpatterns = [
    
    path('grades/add/', GradeCreateView.as_view(), name='grade_add'),
    # السطرين التاليين هما سبب المشكلة (كانا ناقصين):
    path('grades/<int:pk>/edit/', GradeUpdateView.as_view(), name='grade_update'),
    path('grades/<int:pk>/delete/', GradeDeleteView.as_view(), name='grade_delete'),
    
]
