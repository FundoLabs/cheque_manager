# Copyright (c) 2023, BytePanda Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    chequestatuslist = [
        "In Hand",
        "Presented",
        "Cleared",
        "Returned",
        "Returned - Part Paid",
        "Returned - Paid Full",
    ]
    columns = get_columns(filters, chequestatuslist)
    data = get_data(filters, chequestatuslist)

    if not data:
        return columns, []

    return columns, data


def get_data(filters, statuslist):
    chequeconditions = ""
    for status in statuslist:
        chequeconditions += """
            sum(case when chequestatus = "{status}" then 1 else 0 end) as `{status}`,
            sum(case when chequestatus = "{status}" then amount else 0.0 end) as `Amount {status}`,
            """.format(
            status=status
        )

    query = """
		SELECT  
            count(chequestatus) as allcheques,
            sum(amount) as totalamount,
            sum(balance) as totalbalance,
            sum(presented) as clearingattempts,
            sum(case when chequestatus = "Cleared" then presented else 0 end) as clearingattempts,
            {chequeconditions}
            customer,
            salesperson
        FROM `tabCMCheque` group by customer, salesperson
	""".format(
        chequeconditions=chequeconditions
    )

    data = frappe.db.sql(query, as_dict=1)
    for row in data:
        row["clearancerate"] = (
            row["Cleared"]
            * 100
            / (
                row["Cleared"]
                + row["Returned"]
                + row["Returned - Part Paid"]
                + row["Returned - Paid Full"]
            )
        )
        if row["Cleared"] != 0:
            row["avgpresentation"] = row["clearingattempts"] / row["Cleared"]
        else:
            row["avgpresentation"] = 9999
    return data


def get_columns(filters, statuslist):
    columns = [
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "salesperson",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 150,
        },
        {
            "label": _("All Cheques"),
            "fieldname": "allcheques",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": _("Clearance Rate"),
            "fieldname": "clearancerate",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Avg Presentation"),
            "fieldname": "avgpresentation",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Total Amount"),
            "fieldname": "totalamount",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": _("Pending Balance"),
            "fieldname": "totalbalance",
            "fieldtype": "Float",
            "width": 150,
        },
    ]

    for status in statuslist:
        columns.extend(
            [
                {
                    "label": _(status),
                    "fieldname": status,
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "label": _("Amount {}".format(status)),
                    "fieldname": "Amount {}".format(status),
                    "fieldtype": "Float",
                    "width": 150,
                },
            ]
        )

    columns.insert(
        11,
        {
            "label": _("Clearing Attempts"),
            "fieldname": "clearingattempts",
            "fieldtype": "Int",
            "width": 150,
        },
    )
    return columns
