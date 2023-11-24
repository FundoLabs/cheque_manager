# Copyright (c) 2023, BytePanda Technologies Pvt Ltd and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CMTransaction(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cheque: DF.Link | None
		chequeno: DF.Data | None
		comment: DF.SmallText | None
		mode: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		refreturned: DF.Check
		transaction_status: DF.Literal["Paid", "Unpaid"]
		transactionamount: DF.Float
		transactiondate: DF.Date | None
	# end: auto-generated types
	pass
