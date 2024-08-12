# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ExpenseEntry(Document):
	pass

	def on_submit(self):
		doc = frappe.new_doc("Journal Entry")
		doc.posting_date = self.posting_date
		doc.company = self.company
		doc.multi_currency = 1
		doc.title = "Expense Entry"
		amount = 0.0
		for d in self.accounts:
			if d.amount:
				doc.append("accounts", {
						"account": d.account,
						"debit_in_account_currency": d.amount,
						"user_remark": d.remark,
						"cost_center": d.cost_center,
						"department": d.department,
						"project": d.project,
					})
				amount += d.amount
		doc.append("accounts", {
				"account": self.cash_account,
				"credit_in_account_currency": amount,
				"cost_center": d.cost_center,
				"department": d.department,
				"project": d.project,
			})
		doc.expense_entry = self.name
		doc.save(ignore_permissions=True)
		doc.submit()

	def on_cancel(self):
		gl_entries = frappe.db.sql("select name from `tabJournal Entry` where expense_entry = %s",(self.name))
		if gl_entries:
			for d in gl_entries:
				doc = frappe.get_doc("Journal Entry", d[0])
				if doc.docstatus == 1:
					doc.cancel()
				frappe.delete_doc("Journal Entry", d[0])