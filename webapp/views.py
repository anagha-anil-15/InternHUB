from django.shortcuts import render,redirect, get_object_or_404
from Admin_Internship.models import StudentDB,CompanyDB,InternshipPostDB
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import Student,Company,ApplicationDB,SavedInternship,StudentNotification,CompanyReview
import random
import re
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required


def student_page(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_select")

    try:
        student = StudentDB.objects.get(id=student_id)
    except StudentDB.DoesNotExist:
        request.session.flush()
        return redirect("login_select")

    internships = InternshipPostDB.objects.all()

    applied_ids = list(ApplicationDB.objects.filter(student=student).values_list("internship_id", flat=True))
    saved_ids = list(SavedInternship.objects.filter(student=student).values_list("internship_id", flat=True))

    # UNREAD NOTIFICATION COUNT (THIS IS NEW)
    unread_notification_count = StudentNotification.objects.filter(
        student=student,
        is_read=False
    ).count()

    return render(request, "student_template.html", {
        "student": student,
        "internships": internships,
        "applied_ids": applied_ids,
        "saved_ids": saved_ids,
        "unread_notification_count": unread_notification_count,  #  PASS TO TEMPLATE
    })


def company_page(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    total_posts = posts.count()
    total_applications = ApplicationDB.objects.filter(
        internship__in=posts
    ).count()

    shortlisted_count = ApplicationDB.objects.filter(
        internship__in=posts,
        status__iexact="shortlisted"
    ).count()

    #  UNREAD NOTIFICATION COUNT (IMPORTANT)
    unread_notification_count = ApplicationDB.objects.filter(
        internship__in=posts,
        is_seen=False
    ).count()

    return render(request, "company_dashboard1.html", {
        "company": company,
        "posts": posts,
        "total_posts": total_posts,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count,
        "unread_notification_count": unread_notification_count,  #  PASS THIS
    })




def login_select(request):
    return render(request, "login_select.html")


def signup_select(request):
    return render(request, "signup_select.html")




def signup_student(request):
    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        phone = request.POST.get("number")

        # ✅ Phone number validation (10 digits)
        if not re.fullmatch(r"\d{10}", phone):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect("signup_student")

        # ✅ Password match validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup_student")

        # ✅ Password strength validation
        password_pattern = r'^(?=.*[A-Z])(?=.*[\W_]).{6,}$'
        if not re.match(password_pattern, password):
            messages.error(
                request,
                "Password must be at least 6 characters long, contain one uppercase letter and one special character."
            )
            return redirect("signup_student")

        # ✅ Save signup data in session
        request.session["signup_data"] = {
            "type": "student",
            "name": request.POST.get("name"),
            "degree": request.POST.get("degree"),
            "email": request.POST.get("email"),
            "number": phone,
            "skills": request.POST.get("skills"),
            "password": password,
        }

        # ✅ Save files
        resume = request.FILES.get("resume")
        img = request.FILES.get("img")

        fs = FileSystemStorage()
        resume_name = fs.save(resume.name, resume)
        img_name = fs.save(img.name, img)

        request.session["resume"] = resume_name
        request.session["img"] = img_name

        # ✅ Generate OTP
        StudentDB.objects.create(
            name=request.POST.get("name"),
            Degree=request.POST.get("degree"),
            email=request.POST.get("email"),
            number=phone,
            skills=request.POST.get("skills"),
            resume=resume_name,
            img=img_name,
            password=password,
            is_verified=True  # ✅ AUTO VERIFIED
        )

        messages.success(request, "Signup successful! Please login.")
        return redirect("login_select")

    return render(request, "signup_student.html")



def signup_company(request):
    if request.method == "POST":

        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # ✅ Phone validation
        if not re.fullmatch(r"\d{10}", phone):
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect("signup_company")

        # ✅ Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("signup_company")

        # ✅ Password strength
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*[\W_]).{6,}$', password):
            messages.error(
                request,
                "Password must be at least 6 characters long, include one uppercase letter and one special character."
            )
            return redirect("signup_company")

        # ✅ Save data in session
        request.session["signup_data"] = {
            "type": "company",
            "company_name": request.POST.get("company_name"),
            "email": request.POST.get("email"),
            "phone": phone,
            "location": request.POST.get("location"),
            "description": request.POST.get("description"),
            "password": password,
        }

        # ✅ Save logo
        logo = request.FILES.get("logo")
        fs = FileSystemStorage()
        logo_name = fs.save(f"company_logos/{logo.name}", logo)
        request.session["logo"] = logo_name

        CompanyDB.objects.create(
            company_name=request.POST.get("company_name"),
            email=request.POST.get("email"),
            C_phone=phone,
            C_Location=request.POST.get("location"),
            C_Description=request.POST.get("description"),
            logo=logo_name,
            password=password,
            is_verified=True  # ✅ AUTO VERIFIED
        )

        messages.success(request, "Signup successful! Please login.")
        return redirect("login_select")

    return render(request, "signup_company.html")



# def verify_otp(request):
#     if request.method == "POST":
#         otp_input = request.POST.get("otp")
#         otp_session = str(request.session.get("otp"))
#
#         if otp_input == otp_session:
#             signup_data = request.session.get("signup_data")
#             if not signup_data:
#                 messages.error(request, "Session expired. Please signup again.")
#                 return redirect("signup_student")  # or redirect to company signup
#
#             account_type = signup_data.get("type")
#
#             if account_type == "student":
#                 StudentDB.objects.create(
#                     name=signup_data["name"],
#                     Degree=signup_data["degree"],
#                     email=signup_data["email"],
#                     number=signup_data["number"],
#                     skills=signup_data["skills"],
#                     resume=request.session.get("resume"),
#                     img=request.session.get("img"),
#                     password=signup_data["password"],
#                     is_verified=True
#                 )
#
#             elif account_type == "company":
#                 CompanyDB.objects.create(
#                     company_name=signup_data["company_name"],
#                     email=signup_data["email"],
#                     C_phone=signup_data["phone"],
#                     C_Location=signup_data["location"],
#                     C_Description=signup_data["description"],
#                     logo=request.session.get("logo"),
#                     password=signup_data["password"],
#                     is_verified=True
#                 )
#
#             else:
#                 messages.error(request, "Invalid account type.")
#                 return redirect("signup_student")
#
#             # Cleanup session
#             request.session.flush()
#
#             messages.success(request, "Account verified successfully! Please login.")
#             return redirect("login_select")
#
#         else:
#             messages.error(request, "Invalid OTP")
#             return redirect("verify_otp")
#
#     return render(request, "verify_otp.html")






def login(request):
    if request.method == "POST":
        user_type = request.POST["type"]
        email = request.POST["email"]
        password = request.POST["password"]

        if user_type == "student":
            user = StudentDB.objects.filter(
                email=email,
                password=password,
                is_verified=True
            ).first()

            if user:
                request.session["student_id"] = user.id
                request.session["user_type"] = "student"
                messages.success(request, "Login successful")
                return redirect("student_page")

        elif user_type == "company":
            user = CompanyDB.objects.filter(
                email=email,
                password=password,
                is_verified=True
            ).first()

            if user:
                request.session["company_id"] = user.id
                request.session["user_type"] = "company"
                messages.success(request, "Login successful")
                return redirect("company_page")

        messages.error(request, "Invalid credentials or email not verified")

    return redirect("login_select")


def logout_view(request):
    request.session.flush()   # clears all session data
    return redirect("login_select")







# rating
def demo(request):
    return render(request,"DEMO.html")

# apply internship

# views.py





def apply_internship(request, id):

    internship = get_object_or_404(InternshipPostDB, id=id)

    # Get student from session
    student_id = request.session.get("student_id")

    if student_id is None:
        messages.error(request, "Please login first.")
        return redirect(login)

    student = get_object_or_404(StudentDB, id=student_id)

    # Prevent duplicate
    if ApplicationDB.objects.filter(internship=internship, student=student).exists():
        messages.error(request, "Already applied!")
        return redirect(student_page)

    # Create application
    ApplicationDB.objects.create(
        internship=internship,
        student=student,
        status="Applied"
    )

    messages.success(request, "Application submitted successfully!")
    return redirect(student_page)


# save button
def save_internship(request, id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect(login_select)

    student = StudentDB.objects.get(id=student_id)
    internship = InternshipPostDB.objects.get(id=id)

    # Check already saved
    exists = SavedInternship.objects.filter(student=student, internship=internship).exists()

    if not exists:
        SavedInternship.objects.create(student=student, internship=internship)

    return redirect(student_page)

def show_saved_internships(request):
    student_id = request.session.get("student_id")  # FIX: Must match login session key

    if not student_id:
        return redirect("login_select")

    try:
        student = StudentDB.objects.get(id=student_id)
    except StudentDB.DoesNotExist:
        request.session.flush()
        return redirect("login_select")

    saved_items = SavedInternship.objects.filter(student=student)

    return render(request, "saved_internships.html", {
        "student": student,
        "saved_items": saved_items
    })




def confirm_apply(request, id):
    internship = get_object_or_404(InternshipPostDB, id=id)

    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login_select")

    student = get_object_or_404(StudentDB, id=student_id)

    # Prevent duplicate application
    if ApplicationDB.objects.filter(student=student, internship=internship).exists():
        messages.warning(request, "You have already applied for this internship.")
        return redirect("student_page")

    if request.method == "POST":
        # Update contact details if edited
        student.email = request.POST.get("email")
        student.number = request.POST.get("number")
        student.save()

        ApplicationDB.objects.create(
            student=student,
            internship=internship,
            status="Applied"
        )

        messages.success(request, "✅ Application successfully submitted!")
        return redirect("student_page")

    return render(request, "confirm_apply.html", {
        "student": student,
        "internship": internship
    })

def internship_detail(request, id):
    internship = get_object_or_404(InternshipPostDB, id=id)

    student_id = request.session.get("student_id")
    student = None
    saved = False
    applied = False

    if student_id:
        student = StudentDB.objects.get(id=student_id)
        saved = SavedInternship.objects.filter(student=student, internship=internship).exists()
        applied = ApplicationDB.objects.filter(student=student, internship=internship).exists()

    return render(request, "internship_detail.html", {
        "student": student,  # ✅ ADD THIS
        "internship": internship,
        "saved": saved,
        "applied": applied
    })


def my_applications(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_select")

    student = StudentDB.objects.get(id=student_id)

    applications = ApplicationDB.objects.filter(
        student=student
    ).select_related("internship")

    for app in applications:
        app.company = CompanyDB.objects.filter(
            company_name=app.internship.company_name
        ).first()

        # ✅ CHECK IF STUDENT ALREADY RATED THIS COMPANY
        app.is_rated = False
        if app.company:
            app.is_rated = CompanyReview.objects.filter(
                student=student,
                company=app.company
            ).exists()

    # Status counts
    applied_count = applications.filter(status="Applied").count()
    shortlisted_count = applications.filter(status="Shortlisted").count()
    rejected_count = applications.filter(status="Rejected").count()

    return render(request, "my_applications.html", {
        "student": student,
        "applications": applications,
        "applied_count": applied_count,
        "shortlisted_count": shortlisted_count,
        "rejected_count": rejected_count,
    })



def student_settings(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_select")

    student = StudentDB.objects.get(id=student_id)

    if request.method == "POST":
        student.name = request.POST.get("name")
        student.degree = request.POST.get("degree")
        student.email = request.POST.get("email")
        student.number = request.POST.get("number")
        student.skills = request.POST.get("skills")

        if request.FILES.get("resume"):
            student.resume = request.FILES.get("resume")

        if request.FILES.get("img"):
            student.img = request.FILES.get("img")

        student.save()

        # ✅ SUCCESS MESSAGE
        messages.success(request, "Profile updated successfully!")

        return redirect("student_settings")

    return render(request, "student_settings.html", {
        "student": student
    })



def create_internship_post(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    if request.method == "POST":
        InternshipPostDB.objects.create(
            internship_title=request.POST.get("internship_title"),
            company_name=company.company_name,
            location=request.POST.get("location"),
            stipend=request.POST.get("stipend"),
            duration=request.POST.get("duration"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            logo=company.logo
        )

        messages.success(request, "Internship post created successfully!")
        return redirect("company_page")

    # ✅ THIS LINE FIXES NAVBAR + SIDEBAR
    return render(request, "create_internship_post.html", {
        "company": company
    })





def company_applications(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    company_posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    applications = ApplicationDB.objects.filter(
        internship__in=company_posts
    ).select_related("student", "internship")

    # ✅ STATUS COUNTS (FIXED)
    pending_count = applications.filter(status="Pending").count()
    approved_count = applications.filter(status="Approved").count()
    rejected_count = applications.filter(status="Rejected").count()
    shortlisted_count = applications.filter(status="Shortlisted").count()

    return render(request, "company_applications.html", {
        "company": company,
        "applications": applications,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "shortlisted_count": shortlisted_count,
    })






from django.db.models import Avg

def company_details(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    if request.method == "POST":
        company.company_name = request.POST.get("company_name")
        company.email = request.POST.get("email")
        company.C_phone = request.POST.get("phone")
        company.C_Location = request.POST.get("location")
        company.C_Description = request.POST.get("description")
        company.save()

        messages.success(request, "Company details updated successfully!")
        return redirect("company_details")

    # 🔥 POSTS
    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    total_posts = posts.count()
    total_applications = ApplicationDB.objects.filter(
        internship__in=posts
    ).count()

    shortlisted_count = ApplicationDB.objects.filter(
        internship__in=posts,
        status__iexact="shortlisted"
    ).count()

    # 🔔 UNREAD NOTIFICATIONS (THIS WAS MISSING)
    unread_notification_count = ApplicationDB.objects.filter(
        internship__in=posts,
        is_seen=False
    ).count()

    # ⭐ RATINGS
    ratings = CompanyReview.objects.filter(
        company=company
    ).select_related("student").order_by("-created_at")

    avg_rating = ratings.aggregate(avg=Avg("rating"))["avg"]

    return render(request, "company_details.html", {
        "company": company,
        "total_posts": total_posts,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count,
        "ratings": ratings,
        "avg_rating": round(avg_rating, 1) if avg_rating else 0,
        "unread_notification_count": unread_notification_count,  # ✅ ADD THIS
    })



def company_posts(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    #  ONLY this company's posts
    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    return render(request, "company_posts.html", {
        "company": company,
        "posts": posts
    })

def company_post_detail(request, post_id):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    #  Ensure company can see ONLY its own post
    post = get_object_or_404(
        InternshipPostDB,
        id=post_id,
        company_name=company.company_name
    )

    return render(request, "company_post_detail.html", {
        "company": company,
        "post": post
    })
def company_notifications(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    applications = ApplicationDB.objects.filter(
        internship__in=posts
    ).select_related("student", "internship").order_by("-date_applied")

    #  Mark all as seen
    applications.update(is_seen=True)

    return render(request, "company_notifications.html", {
        "applications": applications,
        "company": company
    })

def update_application_status(request, app_id):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    application = get_object_or_404(
        ApplicationDB,
        id=app_id,
        internship__company_name=company.company_name
    )

    new_status = request.GET.get("status")

    if new_status in ["Approved", "Rejected", "Shortlisted"]:
        application.status = new_status
        application.save()

        #  Student notification
        StudentNotification.objects.create(
            student=application.student,
            message=f"You have been {new_status.lower()} for {application.internship.internship_title}"
        )

        messages.success(
            request,
            f"Application {new_status.lower()} successfully."
        )

        #  GO BACK TO SAME PAGE (FIXES YOUR ISSUE)
        return redirect(request.META.get("HTTP_REFERER", "company_applications"))

    return redirect("company_applications")






def rate_company(request, company_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login_select")

    student = StudentDB.objects.get(id=student_id)
    company = CompanyDB.objects.get(id=company_id)

    # Prevent duplicate review
    if CompanyReview.objects.filter(student=student, company=company).exists():
        messages.warning(request, "You already reviewed this company.")
        return redirect("my_applications")

    if request.method == "POST":
        CompanyReview.objects.create(
            student=student,
            company=company,
            rating=request.POST.get("rating"),
            review=request.POST.get("review")
        )

        messages.success(request, "Thanks for your feedback!")
        return redirect("my_applications")

    #  THIS IS THE KEY FIX
    return render(request, "rate_company.html", {
        "company": company
    })



def company_ratings(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    reviews = CompanyReview.objects.filter(company=company)

    return render(request, "company_ratings.html", {
        "company": company,
        "reviews": reviews
    })

def edit_internship_post(request, post_id):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    post = get_object_or_404(
        InternshipPostDB,
        id=post_id,
        company_name=company.company_name
    )

    if request.method == "POST":
        post.internship_title = request.POST.get("internship_title")
        post.location = request.POST.get("location")
        post.duration = request.POST.get("duration")
        post.stipend = request.POST.get("stipend")
        post.description = request.POST.get("description")
        post.is_active = request.POST.get("is_active") == "on"
        post.save()

        messages.success(request, "Internship updated successfully!")
        return redirect("company_posts")

    # ✅ THIS IS THE FIX
    return render(request, "edit_internship_post.html", {
        "post": post,
        "company": company   # 👈 REQUIRED FOR LOGO
    })



def delete_internship_post(request, post_id):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    post = get_object_or_404(
        InternshipPostDB,
        id=post_id,
        company_name=company.company_name
    )

    post.delete()
    messages.success(request, "Internship deleted successfully!")
    return redirect("company_posts")

@require_POST
def remove_saved_internship(request, id):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_select")

    # delete safely (NO 404, NO crash)
    SavedInternship.objects.filter(
        id=id,
        student_id=student_id
    ).delete()

    return redirect("saved_internships")

def student_notifications(request):
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("login_select")

    student = StudentDB.objects.get(id=student_id)

    notifications = StudentNotification.objects.filter(
        student=student
    ).order_by("-created_at")

    # mark all as read
    notifications.update(is_read=True)

    return render(request, "student_notifications.html", {
        "student": student,
        "notifications": notifications
    })

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user_type = request.POST.get("type")

        if user_type == "student":
            user = StudentDB.objects.filter(email=email, is_verified=True).first()
        else:
            user = CompanyDB.objects.filter(email=email, is_verified=True).first()

        if not user:
            messages.error(request, "Email not found.")
            return redirect("forgot_password")

        otp = random.randint(1000, 9999)
        request.session["forgot_otp"] = otp
        request.session["reset_email"] = email
        request.session["reset_type"] = user_type

        send_mail(
            "InternHub Password Reset OTP",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent to your email.")
        return redirect("verify_forgot_otp")

    return render(request, "forgot_password.html")
def verify_forgot_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = str(request.session.get("forgot_otp"))

        if entered_otp == session_otp:
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("verify_forgot_otp")

    return render(request, "verify_forgot_otp.html")
def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        email = request.session.get("reset_email")
        user_type = request.session.get("reset_type")

        if user_type == "student":
            user = StudentDB.objects.get(email=email)
        else:
            user = CompanyDB.objects.get(email=email)

        user.password = password  # (Use hashing later)
        user.save()

        request.session.flush()
        messages.success(request, "Password reset successful. Please login.")
        return redirect("login_select")

    return render(request, "reset_password.html")

