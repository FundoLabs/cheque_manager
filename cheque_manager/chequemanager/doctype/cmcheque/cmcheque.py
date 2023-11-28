# Copyright (c) 2023, BytePanda Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CMCheque(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from cheque_manager.chequemanager.doctype.cmtransaction.cmtransaction import CMTransaction
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Float
        balance: DF.Float
        bank: DF.Link
        chequedate: DF.Date
        chequeno: DF.Data
        chequestatus: DF.Literal["In Hand", "Presented", "Cleared", "Returned", "Returned - Part Paid", "Returned - Paid Full"]
        clearance_date: DF.Date | None
        customer: DF.Link
        customer_name: DF.Data | None
        image: DF.AttachImage | None
        presented: DF.Int
        refcheque: DF.Link | None
        refreturned: DF.Check
        returndate: DF.Date | None
        salesperson: DF.Link
        tocall: DF.Check
        transactions: DF.Table[CMTransaction]
    # end: auto-generated types

    def before_save(self):
        if self.amount == 0.00:
            frappe.throw("Amount cannot be zero")
        if self.chequestatus != "Cleared":
            self.clearance_date = None
        if self.chequestatus in ["In Hand", "Presented", "Cleared"]:
            self.returndate = None

        if self.refreturned:
            if self.refcheque == self.name:
                frappe.throw("This cheque and ref cheque cannot be same")
            self.create_transaction_in_refcheque()

        if self.has_value_changed("chequestatus") and self.chequestatus == "Cleared":
            self.create_transaction()
            if self.refreturned:
                # this has to be called after transactions are created
                self.update_status_in_refcheque()

        if self.has_value_changed("chequestatus") and self.chequestatus == "Presented":
            self.presented += 1

        # recalculate Balance
        self.recalculate_balance()

    def recalculate_balance(self):
        # lets reset and recalculate
        self.balance = self.amount

        # update the balance from transactions as self.amount - sum of CMTransaction amounts
        for transaction in self.transactions:
            if transaction.transaction_status == "Paid":
                self.balance -= transaction.transactionamount

        if self.balance <= 0.0 and self.chequestatus in [
            "Returned",
            "Returned - Part Paid",
        ]:
            self.balance = 0.0
            self.chequestatus = "Returned - Paid Full"
        elif (
            self.balance > 0.0
            and self.balance < self.amount
            and self.chequestatus in ["Returned", "Returned - Part Paid"]
        ):
            self.chequestatus = "Returned - Part Paid"

    def create_transaction(self):
        from datetime import date

        filters = {
            "parent": self.name,
            "chequeno": self.chequeno,
        }
        # check if the CMTransaction doc exists in frappe
        transaction_exists = frappe.db.exists("CMTransaction", filters)
        if transaction_exists is not None:
            transaction_to_update = frappe.get_doc("CMTransaction", transaction_exists)
            transaction_to_update.transaction_status = (
                "Unpaid" if self.chequestatus != "Cleared" else "Paid"
            )
            transaction_to_update.chequeno = self.chequeno
            transaction_to_update.transactionamount = self.amount
            transaction_to_update.refreturned = self.refreturned
            transaction_to_update.save(ignore_permissions=True)
        else:
            new_transaction = frappe.new_doc("CMTransaction")
            new_transaction.parent = self.name
            new_transaction.cheque = self.name
            new_transaction.parenttype = "CMCheque"
            new_transaction.parentfield = "transactions"
            new_transaction.transactiondate = date.today()
            new_transaction.transaction_status = "Paid"
            new_transaction.mode = "Cheque"
            new_transaction.chequeno = self.chequeno
            new_transaction.refreturned = self.refreturned
            new_transaction.transactionamount = self.amount
            self.transactions.append(new_transaction)

    def create_transaction_in_refcheque(self):
        from datetime import date

        filters = {
            "parent": self.refcheque,
            "chequeno": self.chequeno,
        }
        # check if the CMTransaction doc exists in frappe
        transaction_exists = frappe.db.exists("CMTransaction", filters)
        if transaction_exists is not None:
            # get exisiting CMTransaction doc from frappe and update
            transaction_to_update = frappe.get_doc("CMTransaction", transaction_exists)
            transaction_to_update.transaction_status = (
                "Unpaid" if self.chequestatus != "Cleared" else "Paid"
            )
            transaction_to_update.mode = "Cheque"
            transaction_to_update.transactionamount = self.amount
            transaction_to_update.chequeno = self.chequeno
            transaction_to_update.save(ignore_permissions=True)
            # get document for refcheque
            parentcheque = frappe.get_doc("CMCheque", self.refcheque)
            # just invalidating balance. Calculation will be taken care by on_save
            parentcheque.balance = transaction_to_update.transactionamount
            parentcheque.save()
        else:
            # Create new CMTransaction doc from frappe and update in parentcheque
            new_transaction = frappe.new_doc("CMTransaction")
            new_transaction.transaction_status = (
                "Unpaid" if self.chequestatus != "Cleared" else "Paid"
            )
            new_transaction.mode = "Cheque"
            new_transaction.transactionamount = self.amount
            new_transaction.transactiondate = date.today()
            new_transaction.chequeno = self.chequeno
            new_transaction.parent = self.refcheque
            new_transaction.cheque = self.name
            new_transaction.parenttype = "CMCheque"
            new_transaction.parentfield = "transactions"
            # get document for refcheque
            parentcheque = frappe.get_doc("CMCheque", self.refcheque)
            # append into cheque and save
            parentcheque.transactions.append(new_transaction)
            parentcheque.save(ignore_permissions=True)

    def update_status_in_refcheque(self):
        # get document for refcheque
        filters = {
            "parent": self.refcheque,
            "chequeno": self.chequeno,
        }
        # check if the CMTransaction doc exists in frappe
        transaction_exists = frappe.db.exists("CMTransaction", filters)
        if transaction_exists is not None:
            # get exisiting CMTransaction doc from frappe and update status to Paid
            transaction_to_update = frappe.get_doc("CMTransaction", transaction_exists)
            transaction_to_update.transaction_status = "Paid"
            transaction_to_update.save(ignore_permissions=True)
            # get document for refcheque
            parentcheque = frappe.get_doc("CMCheque", self.refcheque)
            # just invalidating balance reset will be taken care by on_save
            parentcheque.balance = transaction_to_update.transactionamount
            parentcheque.save()
