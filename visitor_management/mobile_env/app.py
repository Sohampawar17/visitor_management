import json
import os
import calendar
import requests
import datetime
import frappe
from frappe import _
from frappe.auth import LoginManager
from frappe.utils import (
    cstr,
    get_date_str,
    today,
    nowdate,
    getdate,
    now_datetime,
    get_first_day,
    get_last_day,
    date_diff,
    flt,
    pretty_date,
    fmt_money,
)
from visitor_management.mobile_env.app_utils import (
    gen_response,
    generate_key,
    role_profile,
    ess_validate,
    get_employee_by_user,
    validate_employee_data,
    get_ess_settings,
    get_global_defaults,
    exception_handel,
)

from erpnext.accounts.utils import get_fiscal_year



@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        login_manager.post_login()
        if frappe.response["message"] == "Logged In":
            frappe.response["user"] = login_manager.user
            frappe.response["role_profile"] = role_profile(login_manager.user)  # Add role_profile to the response
            frappe.response["key_details"] = generate_key(login_manager.user)
        gen_response(200, frappe.response["message"])
    except frappe.AuthenticationError:
        gen_response(500, frappe.response["message"])
    except Exception as e:
        return exception_handel(e)


def validate_employee(user):
    if not frappe.db.exists("Employee", dict(user_id=user)):
        frappe.response["message"] = "Please link Employee with this user"
        raise frappe.AuthenticationError(frappe.response["message"])


@frappe.whitelist()
def get_user_document(user_name):
    user_doc = frappe.get_doc("User", user_name)
    return user_doc


@frappe.whitelist()
def info(name):
    token = 'token 697b7b1b7fac426:507ef9f64b1025a'
    
    if name.startswith("TLC"):
        doc_name = "TLC Member Registration"
    else:
        doc_name = "Visitor Information"

    response = requests.get(f'https://tlcbigbash.com/api/resource/{doc_name}/{name}', headers={'Authorization': token})

    if response.status_code == 200:
        frappe.msgprint(response.url)
        data = response.json()

        for i in data:
            responce_data = dict(data[i])
            frappe.msgprint(str(responce_data))
            doc = frappe.new_doc("Event Attendance")
            doc.qr_code_data = responce_data['name']
            doc.name1 = responce_data['full_name'] if name.startswith("TLC") else responce_data['first_name']
            doc.tlc_member = responce_data['tlc_member'] if name.startswith("TLC") else "No"
            doc.insert()
            doc.save()
            # requests.post(f'https://tlcbigbash.com/api/resource/Attendance', headers={'Authorization': token})
            gen_response(200, "Attendance Marked",doc)

            
    else:
        gen_response(500, "Attendance not marked", response.status_code)
   


@frappe.whitelist()
def gift_assign(name):
    token = 'token 697b7b1b7fac426:507ef9f64b1025a'
    
    response = requests.get(f'https://events.erpdata.in/api/resource/TLC Member Registration/{name}', headers={'Authorization': token})

    if response.status_code == 200:
        frappe.msgprint(response.url)
        data = response.json()

        for i in data:
            responce_data = dict(data[i])
            frappe.msgprint(str(responce_data))
            if responce_data['gift_voucher'] != "Yes":
                frappe.db.set_value("TLC Member Registration", responce_data['name'], "gift_voucher", "Yes")
                gen_response(200, "Gift given to this TLC member")
            else:
                gen_response(500, "Gift already given to this TLC member") 