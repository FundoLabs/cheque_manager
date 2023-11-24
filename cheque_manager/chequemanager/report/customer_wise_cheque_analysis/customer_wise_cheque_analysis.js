// Copyright (c) 2023, BytePanda Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Customer-wise Cheque Analysis"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.get_today(),
    },
  ],

  formatter: function (value, row, column, data, default_formatter) {
    var value = default_formatter(value, row, column, data);
    var chequestatuslist = [
      "In Hand",
      "Presented",
      "Cleared",
      "Returned",
      "Returned - Part Paid",
      "Returned - Paid Full",
    ];

    var amountlist = [
      "Amount In Hand",
      "Amount Presented",
      "Amount Cleared",
      "Amount Returned",
      "Amount Returned - Part Paid",
      "Amount Returned - Paid Full",
    ];

    if (
      chequestatuslist.includes(column.fieldname) ||
      amountlist.includes(column.fieldname)
    ) {
      if (!!row && row.length > 1) {
        var fieldname = column.fieldname.replace("Amount ", "");
        var href = `/app/cmcheque?customer=${encodeURIComponent(
          row[1].content
        )}&chequestatus=${encodeURIComponent(fieldname)}`;
        value =
          "<span> <a target='_blank' href='" +
          href +
          "'>" +
          value +
          "</a></span>";
      }
    }

    return value;
  },
};
