from django.shortcuts import render,redirect
from Admin_Internship.models import StudentDB,CompanyDB,InternshipPostDB
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
def index_page(request):
    student=StudentDB.objects.count()
    company=CompanyDB.objects.count()
    internship_post = InternshipPostDB.objects.count()
    return render(request,"index.html",{'student':student,'company':company,'internship_post':internship_post})
def add_student(request):
    return render(request,"Add_Student.html")
def save_student_data(request):
    if request.method=="POST":
        name=request.POST.get('student_name')
        mail=request.POST.get('email')
        mobile=request.POST.get('contact')
        education=request.POST.get('degree')
        skill=request.POST.get('skills')
        resume=request.FILES.get('resume')
        img=request.FILES['img']
        passw=request.POST.get('password')
        c_passw=request.POST.get('confirm_password')
        obj=StudentDB(name=name,email=mail,number=mobile,Degree=education,skills=skill,resume=resume,img=img,password=passw,is_verified=c_passw)
        obj.save()
        return redirect(add_student)
def display_student_data(request):
    data=StudentDB.objects.all()
    return render(request,"display_student_data.html",{'data':data})
def edit_student_data(request,stud_id):
    stud=StudentDB.objects.get(id=stud_id)
    return render(request,"Edit_Student_data.html",{'stud':stud})
def update_student_data(request,up_id):
    if request.method=="POST":
        name = request.POST.get('student_name')
        mail = request.POST.get('email')
        mobile = request.POST.get('contact')
        education = request.POST.get('degree')
        skill = request.POST.get('skills')
        if request.FILES.get('resume'):
            resume=request.FILES
        try:
            img = request.FILES['img']
            fs=FileSystemStorage()
            file=fs.save(img.name,img)
        except MultiValueDictKeyError:
            file=StudentDB.objects.get(id=up_id).img


        passw = request.POST.get('password')
        c_passw = request.POST.get('confirm_password')
        StudentDB.objects.filter(id=up_id).update(name=name,email=mail,number=mobile,Degree=education,skills=skill,resume=file,img=file,password=passw,is_verified=c_passw)
        return redirect(display_student_data)
def delete_student_data(request,del_id):
    data=StudentDB.objects.filter(id=del_id)
    data.delete()
    return redirect(display_student_data)




def add_company(request):
    return render(request,"Add_company.html")
def save_company_data(request):
    if request.method=="POST":
        c_name=request.POST.get('company_name')
        c_mail=request.POST.get('email')
        c_number=request.POST.get('phone')
        c_location=request.POST.get('location')
        c_description=request.POST.get('description')
        logo=request.FILES['logo']
        c_password=request.POST.get('password')
        c_confirm=request.POST.get('confirm_password')
        obj=CompanyDB(company_name=c_name,email=c_mail,C_phone=c_number,C_Location=c_location,C_Description=c_description,logo=logo,password=c_password,is_verified=c_confirm)
        obj.save()
        return redirect(add_company)
def display_company_data(request):
    data=CompanyDB.objects.all()
    return render(request,"display_company_data.html",{'data':data })
def edit_company_data(request,comp_id):
    comp=CompanyDB.objects.get(id=comp_id)
    return render(request,"Edit_Company_data.html",{'comp':comp})
def update_company_data(request,up_id):
    if request.method == "POST":
        c_name = request.POST.get('company_name')
        c_mail = request.POST.get('email')
        c_number = request.POST.get('phone')
        c_location = request.POST.get('location')
        c_description = request.POST.get('description')
        try:
            logo = request.FILES['logo']
            fs=FileSystemStorage()
            file=fs.save(logo.name,logo)
        except MultiValueDictKeyError:
            file=CompanyDB.objects.get(id=up_id).logo

        c_password = request.POST.get('password')
        c_confirm = request.POST.get('confirm_password')
        CompanyDB.objects.filter(id=up_id).update(company_name=c_name,email=c_mail,C_phone=c_number,C_Location=c_location,C_Description=c_description,logo=file,password=c_password,is_verified=c_confirm)
        return redirect(display_company_data)
def delete_company_data(request,del_id):
    data=CompanyDB.objects.filter(id=del_id)
    data.delete()
    return redirect(display_company_data)




def add_internship_post(request):
    return render(request,"Add_InternshipPost.html")
def save_internship_post(request):
    if request.method=="POST":
        title=request.POST.get('internship_title')
        comp_name=request.POST.get('company_name')
        loca=request.POST.get('location')
        salary=request.POST.get('stipend')
        time=request.POST.get('duration')
        desc=request.POST.get('description')
        post=request.POST.get('posted_date')
        image=request.FILES['image']

        obj=InternshipPostDB(internship_title=title,company_name=comp_name,location=loca,stipend=salary,duration=time,description=desc,image=image,posted_date=post)
        obj.save()
        return redirect(add_internship_post)
def display_internship_data(request):
    data=InternshipPostDB.objects.all()
    return render(request,"display_internship.html",{'data':data})
def edit_internship_data(request,post_id):
    post=InternshipPostDB.objects.get(id=post_id)
    return render(request,"Edit_Internship_data.html",{'post':post})
def update_internship_data(request,up_id):
    if request.method=="POST":
        title = request.POST.get('internship_title')
        comp_name = request.POST.get('company_name')
        loca = request.POST.get('location')
        salary = request.POST.get('stipend')
        time = request.POST.get('duration')
        desc = request.POST.get('description')
        post = request.POST.get('posted_date')
        try:
            image = request.FILES['image']
            fs=FileSystemStorage()
            file=fs.save(image.name,image)
        except MultiValueDictKeyError:
            file=InternshipPostDB.objects.get(id=up_id).image

        InternshipPostDB.objects.filter(id=up_id).update(internship_title=title,company_name=comp_name,location=loca,stipend=salary,duration=time,description=desc,image=file,posted_date=post)
        return redirect(display_internship_data)
def delete_internship_data(request,del_id):
    data=InternshipPostDB.objects.filter(id=del_id)
    data.delete()
    return redirect(display_internship_data)

def admin_login_page(request):
    return render(request,"Admin_Login.html")
def admin_login(request):
    if request.method=="POST":
        un=request.POST.get('username')
        pswd=request.POST.get('password')
        if User.objects.filter(username__contains=un).exists():
            data=authenticate(username=un,password=pswd)
            if data is not None:
                login(request,data)
                request.session['username']=un
                request.session['password']=pswd
                return redirect(index_page)
            else:
                return redirect(admin_login_page)
        else:
            return redirect(admin_login_page)
def admin_logout(request):
    del request.session['username']
    del request.session['password']
    return redirect(admin_login_page)