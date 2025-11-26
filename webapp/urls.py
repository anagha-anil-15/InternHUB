from django.urls import path
from webapp import views
urlpatterns=[
    path('student_page/',views.student_page,name="student_page"),
    path('company_page/',views.company_page,name="company_page"),
    path("login/", views.login_select, name="login_select"),
    path("signup/", views.signup_select, name="signup_select"),
    path("signup/student/", views.signup_student, name="signup_student"),
    path("signup/company/", views.signup_company, name="signup_company"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("login/action/", views.login, name="login_action"),
]