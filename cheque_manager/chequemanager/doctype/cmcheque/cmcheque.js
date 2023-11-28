// Copyright (c) 2023, BytePanda Technologies Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("CMCheque", {
  onload(frm) {
    frm.trigger("handle_validate_or_load");
  },
  validate(frm) {
    frm.trigger("handle_validate_or_load");
  },

  customer(frm) {
    frappe.db.get_doc("Customer", frm.doc.customer).then((cust) => {
      frm.doc.customer_name = cust.customer_name;
    });
  },

  handle_validate_or_load(frm) {
    if (frm.doc.chequestatus === "In Hand") {
      set_field_options("chequestatus", ["In Hand", "Presented"]);
    } else if (frm.doc.chequestatus === "Presented") {
      set_field_options("chequestatus", ["Presented", "Cleared", "Returned"]);
    } else if (frm.doc.chequestatus === "Cleared") {
      set_field_options("chequestatus", ["Cleared"]);
      frm.toggle_enable(["chequestatus", "clearance_date"], false);
      frm.disable_save();
    } else if (frm.doc.chequestatus === "Returned") {
      set_field_options("chequestatus", ["In Hand", "Presented", "Returned"]);
    } else if (frm.doc.chequestatus === "Returned - Paid Full") {
      set_field_options("chequestatus", ["Returned - Paid Full"]);
      frm.toggle_enable(["chequestatus", "returndate"], false);
      frm.set_df_property("returndate", "read_only", 1);
      frm.disable_save();
    } else if (frm.doc.chequestatus === "Returned - Part Paid") {
      set_field_options("chequestatus", ["Returned - Part Paid"]);
      frm.toggle_enable(["chequestatus", "returndate"], false);
      frm.set_df_property("returndate", "read_only", 1);
    } else {
      set_field_options("chequestatus", [frm.doc.chequestatus]);
    }
    frm.set_query("refcheque", function () {
      return {
        filters: {
          chequestatus: ["in", ["Returned", "Returned - Part Paid"]],
        },
      };
    });
  },
});
