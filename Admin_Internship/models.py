from django.db import models

class StudentDB(models.Model):
    name=models.CharField(max_length=50,blank=True,null=True)
    email=models.EmailField(max_length=200, null=True, blank=True)
    number=models.IntegerField(blank=True,null=True)
    Degree=models.CharField(max_length=50,blank=True,null=True)
    skills=models.CharField(max_length=50,blank=True,null=True)
    resume=models.FileField(upload_to='resume/',blank=True,null=True)
    img=models.ImageField(upload_to="student_profile",blank=True,null=True)
    password=models.CharField(max_length=50,blank=True,null=True)
    is_verified=models.CharField(max_length=50,blank=True,null=True)
class CompanyDB(models.Model):
    company_name=models.CharField(max_length=50,null=True,blank=True)
    email=models.EmailField(max_length=200, null=True, blank=True)
    C_phone=models.IntegerField(null=True,blank=True)
    C_Location=models.CharField(max_length=50,null=True,blank=True)
    C_Description=models.TextField(null=True,blank=True)
    logo=models.ImageField(upload_to="company_profile",null=True,blank=True)
    password=models.CharField(max_length=50,null=True,blank=True)
    is_verified=models.CharField(max_length=50,null=True,blank=True)
class InternshipPostDB(models.Model):
    internship_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=150)
    stipend = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    description = models.TextField()
    posted_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='internship_images/', null=True, blank=True)
    logo = models.ImageField(upload_to='Company_Logo/', null=True, blank=True)


# Create your models here.
