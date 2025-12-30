from django.shortcuts import render,redirect, get_object_or_404
from Admin_Internship.models import StudentDB,CompanyDB,InternshipPostDB
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import Student,Company,ApplicationDB,SavedInternship
import random
from django.contrib.auth.decorators import login_required


def student_page(request):
    student_id = request.session.get("student_id")  # use correct key

    if not student_id:
        return redirect("login_select")

    try:
        student = StudentDB.objects.get(id=student_id)
    except StudentDB.DoesNotExist:
        request.session.flush()  # clear wrong session
        return redirect("login_select")


    internships = InternshipPostDB.objects.all()

    applied_ids = list(ApplicationDB.objects.filter(student=student).values_list("internship_id", flat=True))
    saved_ids = list(SavedInternship.objects.filter(student=student).values_list("internship_id", flat=True))

    return render(request, "student_template.html", {
        "student": student,
        "internships": internships,
        "applied_ids": applied_ids,
        "saved_ids": saved_ids,
    })

def company_page(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    # 🔹 Company posts
    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    # 🔹 Total posts
    total_posts = posts.count()

    # 🔹 Total applications for company posts
    total_applications = ApplicationDB.objects.filter(
        internship__in=posts
    ).count()

    # 🔹 Shortlisted applications
    shortlisted_count = ApplicationDB.objects.filter(
        internship__in=posts,
        status__iexact="shortlisted"
    ).count()

    # 🔔 Unseen notifications
    notification_count = ApplicationDB.objects.filter(
        internship__in=posts,
        is_seen=False
    ).count()

    return render(request, "company_dashboard1.html", {
        "company": company,
        "posts": posts,
        "total_posts": total_posts,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count,
        "notification_count": notification_count,
    })



def login_select(request):
    return render(request, "login_select.html")


def signup_select(request):
    return render(request, "signup_select.html")


def signup_student(request):
    if request.method == "POST":
        if request.POST["password"] != request.POST["confirm_password"]:
            messages.error(request, "Passwords do not match")
            return redirect("signup_student")

        request.session["signup_data"] = {
            "type": "student",
            "name": request.POST["name"],
            "degree": request.POST["degree"],
            "email": request.POST["email"],
            "number": request.POST["number"],
            "skills": request.POST["skills"],
            "password": request.POST["password"],
        }

        # Save files temporarily in session
        request.session["resume"] = request.FILES["resume"].name
        request.session["img"] = request.FILES["img"].name

        # Store files in MEDIA
        from django.core.files.storage import FileSystemStorage
        fs = FileSystemStorage()
        fs.save(request.FILES["resume"].name, request.FILES["resume"])
        fs.save(request.FILES["img"].name, request.FILES["img"])

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
        if request.POST["password"] != request.POST["confirm_password"]:
            messages.error(request, "Passwords do not match")
            return redirect("signup_company")

        # Save form data temporarily in session (OTP flow)
        request.session["company_signup"] = {
            "company_name": request.POST["company_name"],
            "email": request.POST["email"],
            "phone": request.POST["phone"],
            "location": request.POST["location"],
            "description": request.POST["description"],
            "password": request.POST["password"],
        }

        # Save logo
        request.session["logo"] = request.FILES["logo"].name
        from django.core.files.storage import FileSystemStorage
        fs = FileSystemStorage()
        fs.save(request.FILES["logo"].name, request.FILES["logo"])

        # OTP
        otp = random.randint(1000, 9999)
        request.session["otp"] = otp

        send_mail(
            "InternHub OTP Verification",
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

            # ---------- STUDENT SIGNUP ----------
            if "signup_data" in request.session:
                data = request.session.get("signup_data")

                StudentDB.objects.create(
                    name=data["name"],
                    Degree=data["degree"],
                    email=data["email"],
                    number=data["number"],
                    skills=data["skills"],
                    resume=request.session["resume"],
                    img=request.session["img"],
                    password=data["password"],
                    is_verified=True
                )

            # ---------- COMPANY SIGNUP ----------
            elif "company_signup" in request.session:
                data = request.session.get("company_signup")

                CompanyDB.objects.create(
                    company_name=data["company_name"],
                    email=data["email"],
                    C_phone=data["phone"],
                    C_Location=data["location"],
                    C_Description=data["description"],
                    logo=request.session.get("logo"),
                    password=data["password"],
                    is_verified=True
                )

            # cleanup session
            request.session.flush()

            messages.success(request, "Account verified successfully! Please login.")
            return redirect("login_select")

        messages.error(request, "Invalid OTP")
        return redirect("verify_otp")

    return render(request, "verify_otp.html")





def login(request):
    if request.method == "POST":
        user_type = request.POST["type"]
        email = request.POST["email"]
        password = request.POST["password"]

        # STUDENT LOGIN
        if user_type == "student":
            user = StudentDB.objects.filter(
                email=email,
                password=password,
                is_verified=True
            ).first()

            if user:
                request.session["student_id"] = user.id
                request.session["user_type"] = "student"
                return redirect("student_page")  # ✅ FIX


        # COMPANY LOGIN
        elif user_type == "company":
            user = CompanyDB.objects.filter(email=email, password=password, is_verified=True).first()
            if user:
                request.session["company_id"] = user.id
                request.session["user_type"] = "company"
                return redirect(company_page)

        messages.error(request, "Invalid credentials or email not verified")

    return redirect(login_select)
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

    return render(request, "my_applications.html", {
        "student": student,
        "applications": applications
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
            company_name=company.company_name,   # saved in InternshipPostDB
            location=request.POST.get("location"),
            stipend=request.POST.get("stipend"),
            duration=request.POST.get("duration"),
            description=request.POST.get("description"),
            image=request.FILES.get("image"),
            logo=company.logo                   # saved in InternshipPostDB
        )

        messages.success(request, "Internship post created successfully!")
        return redirect("company_page")

    return render(request, "create_internship_post.html")




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




def company_details(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    # ✅ Handle Edit
    if request.method == "POST":
        company.company_name = request.POST.get("company_name")
        company.email = request.POST.get("email")
        company.C_phone = request.POST.get("phone")
        company.C_Location = request.POST.get("location")
        company.C_Description = request.POST.get("description")
        company.save()

        messages.success(request, "Company details updated successfully!")
        return redirect("company_details")

    # 🔥 GET COMPANY POSTS (SOURCE OF TRUTH)
    posts = InternshipPostDB.objects.filter(
        company_name=company.company_name
    )

    # 📊 ANALYTICS (FIXED)
    total_posts = posts.count()

    total_applications = ApplicationDB.objects.filter(
        internship__in=posts
    ).count()

    shortlisted_count = ApplicationDB.objects.filter(
        internship__in=posts,
        status__iexact="shortlisted"
    ).count()

    # # ⭐ RATINGS
    # ratings = CompanyRating.objects.filter(company=company)
    # avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"]

    return render(request, "company_details.html", {
        "company": company,
        "total_posts": total_posts,
        "total_applications": total_applications,
        "shortlisted_count": shortlisted_count,
        # "ratings": ratings,
        # "avg_rating": avg_rating,
    })

def company_posts(request):
    company_id = request.session.get("company_id")

    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)

    # 🔥 ONLY this company's posts
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

    # 🔒 Ensure company can see ONLY its own post
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

    # 🔔 Mark all as seen
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

    # ✅ ONE-CLICK APPROVE / REJECT
    new_status = request.GET.get("status")

    if new_status in ["Approved", "Rejected"]:
        application.status = new_status
        application.save()

        messages.success(
            request,
            f"Application {new_status.lower()} successfully."
        )
        return redirect("company_applications")

    # fallback (manual update page)
    if request.method == "POST":
        application.status = request.POST.get("status")
        application.company_note = request.POST.get("company_note")
        application.save()

        messages.success(request, "Application updated successfully.")
        return redirect("company_applications")

    return render(request, "update_application.html", {
        "application": application
    })


def rate_company(request, company_id):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("login_select")

    student = StudentDB.objects.get(id=student_id)
    company = CompanyDB.objects.get(id=company_id)

    # Prevent duplicate rating
    existing = CompanyRating.objects.filter(student=student, company=company).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        review = request.POST.get("review")

        if existing:
            messages.warning(request, "You already rated this company.")
            return redirect("student_page")

        CompanyRating.objects.create(
            student=student,
            company=company,
            rating=rating,
            review=review
        )

        messages.success(request, "Thanks for your feedback!")
        return redirect("student_page")

    return render(request, "rate_company.html", {
        "company": company
    })

def company_ratings(request):
    company_id = request.session.get("company_id")
    if not company_id:
        return redirect("login_select")

    company = CompanyDB.objects.get(id=company_id)
    ratings = CompanyRating.objects.filter(company=company)

    return render(request, "company_ratings.html", {
        "ratings": ratings,
        "company": company
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
@login_required
def remove_saved_internship(request, id):
    if request.method == "POST":
        # Get logged-in student's StudentDB
        student = get_object_or_404(StudentDB, email=request.user.email)

        saved = get_object_or_404(
            SavedInternship,
            id=id,
            student=student
        )
        saved.delete()

    return redirect('saved_internships')


