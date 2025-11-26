from django.shortcuts import render,redirect
from Admin_Internship.models import StudentDB,CompanyDB,InternshipPostDB
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

import random

def student_page(request):
    student=StudentDB.objects.all()
    return render(request,"student_template.html",{'student':student})
def company_page(request):
    return render(request,"company_dashboard1.html")

def login_select(request):
    return render(request, "login_select.html")


def signup_select(request):
    return render(request, "signup_select.html")


def signup_student(request):
    if request.method == "POST":
        request.session["signup_data"] = {
            "type": "student",
            "name": request.POST["name"],
            "email": request.POST["email"],
            "password": request.POST["password"],
        }
        otp = random.randint(1000, 9999)
        request.session["otp"] = otp

        send_mail(
            "InternHub OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [request.POST["email"]],
            fail_silently=False,
        )

        return redirect("verify_otp")

    return render(request, "signup_student.html")


def signup_company(request):
    if request.method == "POST":
        request.session["signup_data"] = {
            "type": "company",
            "company_name": request.POST["company_name"],
            "email": request.POST["email"],
            "password": request.POST["password"],
        }
        otp = random.randint(1000, 9999)
        request.session["otp"] = otp

        send_mail(
            "InternHub OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [request.POST["email"]],
            fail_silently=False,
        )

        return redirect("verify_otp")

    return render(request, "signup_company.html")


def verify_otp(request):
    if request.method == "POST":
        if request.POST["otp"] == str(request.session.get("otp")):

            data = request.session.get("signup_data")

            if data["type"] == "student":
                StudentDB.objects.create(name=data["name"], email=data["email"], password=data["password"], is_verified=True)
            else:
                CompanyDB.objects.create(company_name=data["company_name"], email=data["email"], password=data["password"], is_verified=True)

            messages.success(request, "Account Verified! Now login.")
            return redirect("login_select")

        messages.error(request, "Invalid OTP")
        return redirect("verify_otp")

    return render(request, "verify_otp.html")



def login(request):
    if request.method == "POST":
        user_type = request.POST["type"]
        email = request.POST["email"]
        password = request.POST["password"]

        if user_type == "student":
            user = StudentDB.objects.filter(email=email, password=password, is_verified=True).first()
            if user:
                request.session["user_id"] = user.id
                request.session["user_type"] = "student"
                return redirect(student_page)

        elif user_type == "company":
            user = CompanyDB.objects.filter(email=email, password=password, is_verified=True).first()
            if user:
                request.session["user_id"] = user.id
                request.session["user_type"] = "company"
                return redirect("company_dashboard")

        messages.error(request, "Invalid credentials or email not verified")

    return redirect("login_select")
