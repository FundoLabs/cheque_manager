frappe.listview_settings["CMCheque"] = {
  hide_name_column: true,
  refresh(listview) {
    let doctypetitle = "Cheque Register";
    listview.page.set_title(doctypetitle);

    frappe.breadcrumbs.clear();
    listview.page.clear_primary_action();

    if (listview.can_create && !frappe.boot.read_only) {
      const doctype_name = "Cheque Entry";

      // Better style would be __("Add {0}", [doctype_name], "Primary action in list view")
      // Keeping it like this to not disrupt existing translations
      const label = `${__(
        "Add",
        null,
        "Primary action in list view"
      )} ${doctype_name}`;
      listview.page.set_primary_action(
        label,
        () => {
          if (listview.settings.primary_action) {
            listview.settings.primary_action();
          } else {
            listview.make_new_doc();
          }
        },
        "add"
      );
    } else {
      listview.page.clear_primary_action();
    }
    frappe.breadcrumbs.append_breadcrumb_element(
      `/app/${cur_list.doctype.toLowerCase()}`,
      doctypetitle
    );
  },
  onload(listview) {
    //   button = listview.parent.getElementsByClassName("sidebar-toggle-btn");
    //   button[0].hidden = true;
    //   listview.page.sidebar.hide();
  },
};
