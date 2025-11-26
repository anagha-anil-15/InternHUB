from django.urls import path
from Admin_Internship import views
urlpatterns=[
    path('index_page/',views.index_page,name="index_page"),
    path('add_student/',views.add_student,name="add_student"),
    path('save_student_data/',views.save_student_data,name="save_student_data"),
    path('display_student_data/',views.display_student_data,name="display_student_data"),
    path('edit_student_data/<int:stud_id>/',views.edit_student_data,name="edit_student_data"),
    path('update_student_data/<int:up_id>/',views.update_student_data,name="update_student_data"),
    path('delete_student_data/<int:del_id>/',views.delete_student_data,name="delete_student_data"),
    path('add_company/',views.add_company,name="add_company"),
    path('save_company_data/',views.save_company_data,name="save_company_data"),
    path('display_company_data/',views.display_company_data,name="display_company_data"),
    path('edit_company_data/<int:comp_id>/',views.edit_company_data,name="edit_company_data"),
    path('update_company_data/<int:up_id>/',views.update_company_data,name="update_company_data"),
    path('delete_company_data/<int:del_id>/',views.delete_company_data,name="delete_company_data"),
    path('add_internship_post/',views.add_internship_post,name="add_internship_post"),
    path('save_internship_post/',views.save_internship_post,name="save_internship_post"),
    path('display_internship_data/',views.display_internship_data,name="display_internship_data"),
    path('edit_internship_data/<int:post_id>/',views.edit_internship_data,name="edit_internship_data"),
    path('update_internship_data/<int:up_id>/',views.update_internship_data,name="update_internship_data"),
    path('delete_internship_data/<int:del_id>/',views.delete_internship_data,name="delete_internship_data"),
    path('admin_login_page/',views.admin_login_page,name="admin_login_page"),
    path('admin_login/',views.admin_login,name="admin_login"),
    path('admin_logout/',views.admin_logout,name="admin_logout"),


]