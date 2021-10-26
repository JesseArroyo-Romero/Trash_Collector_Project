from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import NullBooleanField
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.apps import apps
from django.urls.base import reverse
import calendar




from .models import Employee

# Create your views here.

# TODO: Create a function for each path created in employees/urls.py. Each will need a template as well.

@login_required
def index(request):
    # This line will get the Customer model from the other app, it can now be used to query the db for Customers
    Customer = apps.get_model('customers.Customer')
    logged_in_user = request.user

    try:
        # This line will return the employee record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=logged_in_user)
        customers_by_zip = Customer.objects.filter(zip_code__contains=logged_in_employee.zip_code)
        my_date = date.today()
        day = calendar.day_name[my_date.weekday()]
        customers_by_weekly_pickup = customers_by_zip.filter(weekly_pickup=day) | customers_by_zip.filter(one_time_pickup=my_date)
        active_accounts = customers_by_weekly_pickup.exclude(suspend_start__lte=my_date, suspend_end__gt=my_date)
        picked_up = ''
        context = {
            'customers_by_weekly_pickup': customers_by_weekly_pickup,
            'logged_in_employee': logged_in_employee,
            'my_date': my_date,
            'active_accounts': active_accounts
        }
        return render(request, 'employees/index.html', context)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('employees:create'))
    

    

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
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
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

    
def details(request, user_id):
    customer = Customer.objects.get(pk=user_id)
    context = {
        'customer': customer
    }
    return render(request, 'employees/details.html', context)