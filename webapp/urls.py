from django.urls import path
from webapp import views
urlpatterns=[
    path('student_page/',views.student_page,name="student_page"),
    path('company_page/',views.company_page,name="company_page"),
    path("login/", views.login_select, name="login_select"),
    path("signup/", views.signup_select, name="signup_select"),
    path("signup/student/", views.signup_student, name="signup_student"),
    path("signup/company/", views.signup_company, name="signup_company"),

    path("login/action/", views.login, name="login_action"),
    path("logout/", views.logout_view, name="logout"),
    path("demo/", views.demo, name="demo"),
    path('apply/<int:id>/', views.apply_internship, name='apply_internship'),
    path("save/<int:id>/", views.save_internship, name="save_internship"),
    path("saved-internships/", views.show_saved_internships, name="saved_internships"),
    path('apply/confirm/<int:id>/', views.confirm_apply, name='confirm_apply'),
    path('student/dashboard/', views.student_page, name='student_page'),
    path('internship/<int:id>/', views.internship_detail, name='internship_detail'),
    path("my-applications/", views.my_applications, name="my_applications"),
    path("student/settings/", views.student_settings, name="student_settings"),
    path("company/create-post/", views.create_internship_post, name="create_internship_post"),
    path("company/applications/", views.company_applications, name="company_applications"),
    path("company-details/", views.company_details, name="company_details"),
    path("company-posts/", views.company_posts, name="company_posts"),
    path("company-post/<int:post_id>/",views.company_post_detail,name="company_post_detail"),
    path("company-notifications/", views.company_notifications, name="company_notifications"),
    path("update-application/<int:app_id>/",views.update_application_status,name="update_application_status"),
    path("rate-company/<int:company_id>/", views.rate_company, name="rate_company"),
    path("company-post/edit/<int:post_id>/", views.edit_internship_post, name="edit_internship_post"),
    path("company-post/delete/<int:post_id>/", views.delete_internship_post, name="delete_internship_post"),
    path("saved/remove/<int:id>/",views.remove_saved_internship,name="remove_saved_internship"),
    path("student/notifications/", views.student_notifications, name="student_notifications"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("verify-forgot-otp/", views.verify_forgot_otp, name="verify_forgot_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),



]

