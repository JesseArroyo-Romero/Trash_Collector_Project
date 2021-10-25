from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from django.urls.base import reverse

from .models import Employee

# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    return render(request, 'employees/index.html')

@login_required
def create(request):
    logged_in_employee = request.user
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        department_from_form = request.POST.get('department')
        role_from_form = request.POST.get('role')
        email_from_form = request.POST.get('email')
        new_employee = Employee(name=name_from_form, user=logged_in_employee, address=address_from_form, zip_code=zip_from_form, department=department_from_form, role=role_from_form, email=email_from_form)
        new_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_employee = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_employee)
    if request.method == "POST":
        name_from_form = request.POST.get('name')
        address_from_form = request.POST.get('address')
        zip_from_form = request.POST.get('zip_code')
        department_from_form = request.POST.get('department')
        role_from_form = request.POST.get('role')
        email_from_form = request.POST.get('email')
        logged_in_employee.name = name_from_form
        logged_in_employee.address = address_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.department = department_from_form
        logged_in_employee.role = role_from_form
        logged_in_employee.email = email_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)