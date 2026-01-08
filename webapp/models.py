from django.db import models
from django.contrib.auth.models import User
from Admin_Internship.models import StudentDB,InternshipPostDB,CompanyDB
from django.db.models import Avg
class Student(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Company(models.Model):
    company_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

# Apply Internship

class ApplicationDB(models.Model):
    internship = models.ForeignKey(
        "Admin_Internship.InternshipPostDB",
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        "Admin_Internship.StudentDB",
        on_delete=models.CASCADE
    )

    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Applied"
    )

    # 📝 Written information by company
    company_note = models.TextField(blank=True, null=True)

    date_applied = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.internship.internship_title}"



# save button
class SavedInternship(models.Model):
    student = models.ForeignKey(StudentDB, on_delete=models.CASCADE)
    internship = models.ForeignKey(InternshipPostDB, on_delete=models.CASCADE)
    saved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} saved {self.internship.internship_title}"

class CompanyReview(models.Model):
    student = models.ForeignKey(StudentDB, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyDB, on_delete=models.CASCADE)
    rating = models.IntegerField()   # 1 to 5
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "company")

    def __str__(self):
        return f"{self.student.name} - {self.company.company_name}"


class StudentNotification(models.Model):
    student = models.ForeignKey(StudentDB, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.message}"
