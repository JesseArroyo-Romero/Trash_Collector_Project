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
Customer = apps.get_model('customers.Customer')

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
        final_customers = active_accounts.exclude(date_of_last_pickup=my_date)
        context = {
            'logged_in_employee': logged_in_employee,
            'my_date': my_date,
            'final_customers': final_customers
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
    Customer = apps.get_model('customers.Customer')
    customer = Customer.objects.get(pk=user_id)
    context = {
        'customer': customer
    }
    return render(request, 'employees/details.html', context)

def confirm_pickup(request, customer_id):
    Customer = apps.get_model('customers.Customer')
    person = Customer.objects.get(pk=customer_id)   
    person.date_of_last_pickup = date.today()
    person.balance += 20
    person.save()
    return HttpResponseRedirect(reverse('employees:index'))
 
def weekly_pickup(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    Customer = apps.get_model('customers.Customer')
    my_date = date.today()
    day = calendar.day_name[my_date.weekday()]
    customers_by_zip = Customer.objects.filter(zip_code__contains=logged_in_employee.zip_code) #This gets all the customers whos zip code matches that of the logged in employee
    customers_by_weekly_pickup = customers_by_zip.filter(weekly_pickup=day) | customers_by_zip.filter(one_time_pickup=my_date) #This filters through the above list and only saves the customers whose pickup day is today
    active_accounts = customers_by_weekly_pickup.exclude(suspend_start__lte=my_date, suspend_end__gt=my_date)#This will take out any customer whose pick up is today and their account is suspended
    final_customers = active_accounts.exclude(date_of_last_pickup=my_date)# This will exclude anyone whos trash pickup has been confirmed.
    day_of_week = request.POST.get("weekly_pickup")
    customers = Customer.objects.filter(weekly_pickup=day_of_week) & Customer.objects.filter(zip_code__contains=logged_in_employee.zip_code)
    context = {
        'logged_in_employee': logged_in_employee,
        'my_date': my_date,
        'final_customers': final_customers,
        'final_customers': customers
    }
    return render(request, 'employees/index.html', context)
    