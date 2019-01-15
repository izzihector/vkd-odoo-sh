# -*- coding: utf-8 -*-

import logging
import datetime
import time
import traceback
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta

_logger = logging.getLogger(__name__)

class VKDataSaleSubscriptionTemplate(models.Model):
	_inherit = "sale.subscription.template"

	offset_invoice_generation = fields.Char(string="Offset invoice generation", help="Number of days before or after the subscription period start the invoice should be generated. Can be a positive or a negative number.", required=True, default='0')
	offset_invoice_date = fields.Char(string="Offset invoice date", help="Number of days before or after the subscription period start the invoice date should be set. Can be a positive or a negative number.", required=True, default='0')
	use_subscription_period_end = fields.Boolean(help="Use the subscription period end date, instead of the start date, to calculate the offset. This can be useful when the customer should be billed after the service has been provided.")
	offset_invoice = fields.Boolean(string="Offset invoices", help="This will enable settings that allow you to offset the invoice generation date and the date displayed on the invoice.")
	team_id = fields.Many2one('crm.team', string='Sales Team')

class VKDataExtendedSaleSubscription(models.Model):
	_inherit = 'sale.subscription'

	internal_remarks = fields.Text(string="Internal remarks", track_visibility='always')
	offset_invoice_generation = fields.Char(help="Number of days before or after the subscription period start the invoice should be generated. Can be a positive or a negative number.", required=True, default='0')
	offset_invoice_date = fields.Char(help="Number of days before or after the subscription period start the invoice date should be set. Can be a positive or a negative number.", required=True, default='0')
	use_subscription_period_end = fields.Boolean(help="Use the subscription period end date, instead of the start date, to calculate the offset. This can be useful when the customer should be billed after the service has been provided.")
	offset_specific_subscription = fields.Boolean(string="Offset invoice for this subscription", help="Enable this if you don't want to use the template offset settings, and set the offset for this specific subscription. If this field is disabled, the offset settings from the template will be used instead.")
	new_invoice_generation_date = fields.Date()
	new_invoice_date = fields.Date()
	team_id = fields.Many2one('crm.team', string='Sales Team')

	@api.onchange('template_id')
	def _get_template_team(self):
		self.team_id = self.template_id.team_id

	def _update_existing_subscriptions(self):
		sale_subscription = self.env['sale.subscription'].search([])
		for r in sale_subscription:
			r.team_id = r.template_id.team_id

	def _get_new_invoice_date(self):
		for r in self:
			compute_date = fields.Date.from_string(r.recurring_next_date)
			use_last_date = False
			if r.offset_specific_subscription:
				offset = r.offset_invoice_date
				use_last_date = r.use_subscription_period_end
			elif r.template_id.offset_invoice:
				offset = r.template_id.offset_invoice_date
				use_last_date = r.template_id.use_subscription_period_end
			else:
				r.new_invoice_date = r.recurring_next_date
				return r.new_invoice_date
			if use_last_date:
				next_date = fields.Date.from_string(r.recurring_next_date)
				periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
				end_date = next_date + relativedelta(**{periods[r.recurring_rule_type]: r.recurring_interval})
				end_date = end_date - relativedelta(days=1)
				compute_date = end_date
			r.new_invoice_date = compute_date + timedelta(days=int(offset))
			return r.new_invoice_date

	def _get_new_invoice_generation_date(self):
		for r in self:
			compute_date = fields.Date.from_string(r.recurring_next_date)
			use_last_date = False
			if r.offset_specific_subscription:
				offset = r.offset_invoice_generation
				use_last_date = r.use_subscription_period_end
			elif r.template_id.offset_invoice:
				offset = r.template_id.offset_invoice_generation
				use_last_date = r.template_id.use_subscription_period_end
			else:
				r.new_invoice_generation_date = r.recurring_next_date
				return r.new_invoice_generation_date
			if use_last_date:
				next_date = fields.Date.from_string(r.recurring_next_date)
				periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
				end_date = next_date + relativedelta(**{periods[r.recurring_rule_type]: r.recurring_interval})
				end_date = end_date - relativedelta(days=1)
				compute_date = end_date
			r.new_invoice_generation_date = compute_date + timedelta(days=int(offset))
			return r.new_invoice_generation_date

	# Override entire method, as we need to modify parts in the middle.
	@api.multi
	def _recurring_create_invoice(self, automatic=False):
		super(VKDataExtendedSaleSubscription, self)
		auto_commit = self.env.context.get('auto_commit', True)
		subs = self.env['sale.subscription'].search([])
		cr = self.env.cr
		invoices = self.env['account.invoice']
		current_date = time.strftime('%Y-%m-%d')
		imd_res = self.env['ir.model.data']
		template_res = self.env['mail.template']
		for r in subs:
			r.new_invoice_date = r._get_new_invoice_date()
			r.new_invoice_generation_date = r._get_new_invoice_generation_date()
		if len(self) > 0:
			subscriptions = self
		else:
			domain = [('new_invoice_generation_date', '<=', current_date),
						('state', 'in', ['open', 'pending'])]
			subscriptions = self.search(domain)
		if subscriptions:
			sub_data = subscriptions.read(fields=['id', 'company_id'])
			for company_id in set(data['company_id'][0] for data in sub_data):
				sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
				subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
				context_company = dict(self.env.context, company_id=company_id, force_company=company_id)
				for subscription in subs:
					subscription = subscription[0]  # Trick to not prefetch other subscriptions, as the cache is currently invalidated at each iteration
					if automatic and auto_commit:
						cr.commit()
					# payment + invoice (only by cron)
					if subscription.template_id.payment_mandatory and subscription.recurring_total and automatic:
						try:
							payment_token = subscription.payment_token_id
							tx = None
							if payment_token:
								invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
								new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
								new_invoice.message_post_with_view('mail.message_origin_link',
									values = {'self': new_invoice, 'origin': subscription},
									subtype_id = self.env.ref('mail.mt_note').id)
								tx = subscription._do_payment(payment_token, new_invoice, two_steps_sec=False)[0]
								# commit change as soon as we try the payment so we have a trace somewhere
								if auto_commit:
									cr.commit()
								if tx.state in ['done', 'authorized']:
									subscription.send_success_mail(tx, new_invoice)
									msg_body = 'Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.invoice data-oe-id=%d>View Invoice</a>.' % (tx.id, tx.reference, tx.amount, new_invoice.id)
									subscription.message_post(body=msg_body)
									if auto_commit:
										cr.commit()
								else:
									_logger.error('Fail to create recurring invoice for subscription %s', subscription.code)
									if auto_commit:
										cr.rollback()
									new_invoice.unlink()
							if tx is None or tx.state != 'done':
								amount = subscription.recurring_total
								date_close = datetime.datetime.strptime(subscription.recurring_next_date, "%Y-%m-%d") + relativedelta(days=15)
								close_subscription = current_date >= date_close.strftime('%Y-%m-%d')
								email_context = self.env.context.copy()
								email_context.update({
									'payment_token': subscription.payment_token_id and subscription.payment_token_id.name,
									'renewed': False,
									'total_amount': amount,
									'email_to': subscription.partner_id.email,
									'code': subscription.code,
									'currency': subscription.pricelist_id.currency_id.name,
									'date_end': subscription.date,
									'date_close': date_close.date()
								})
								if close_subscription:
									_, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_close')
									template = template_res.browse(template_id)
									template.with_context(email_context).send_mail(subscription.id)
									_logger.debug("Sending Subscription Closure Mail to %s for subscription %s and closing subscription", subscription.partner_id.email, subscription.id)
									msg_body = 'Automatic payment failed after multiple attempts. Subscription closed automatically.'
									subscription.message_post(body=msg_body)
								else:
									_, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_reminder')
									msg_body = 'Automatic payment failed. Subscription set to "To Renew".'
									if (datetime.datetime.today() - datetime.datetime.strptime(subscription.recurring_next_date, '%Y-%m-%d')).days in [0, 3, 7, 14]:
										template = template_res.browse(template_id)
										template.with_context(email_context).send_mail(subscription.id)
										_logger.debug("Sending Payment Failure Mail to %s for subscription %s and setting subscription to pending", subscription.partner_id.email, subscription.id)
										msg_body += ' E-mail sent to customer.'
									subscription.message_post(body=msg_body)
								subscription.write({'state': 'close' if close_subscription else 'pending'})
							if auto_commit:
								cr.commit()
						except Exception:
							if auto_commit:
								cr.rollback()
							# we assume that the payment is run only once a day
							traceback_message = traceback.format_exc()
							_logger.error(traceback_message)
							last_tx = self.env['payment.transaction'].search([('reference', 'like', 'SUBSCRIPTION-%s-%s' % (subscription.id, datetime.date.today().strftime('%y%m%d')))], limit=1)
							error_message = "Error during renewal of subscription %s (%s)" % (subscription.code, 'Payment recorded: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment recorded.')
							_logger.error(error_message)

					# invoice only
					else:
						try:
							invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
							new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
							new_invoice.message_post_with_view('mail.message_origin_link',
								values = {'self': new_invoice, 'origin': subscription},
								subtype_id = self.env.ref('mail.mt_note').id)
							new_invoice.with_context(context_company).compute_taxes()
							invoices += new_invoice
							next_date = datetime.datetime.strptime(subscription.recurring_next_date or current_date, "%Y-%m-%d")
							periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
							invoicing_period = relativedelta(**{periods[subscription.recurring_rule_type]: subscription.recurring_interval})
							new_date = next_date + invoicing_period
							subscription.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
							if automatic and auto_commit:
								cr.commit()
						except Exception:
							if automatic and auto_commit:
								cr.rollback()
								_logger.exception('Fail to create recurring invoice for subscription %s', subscription.code)
							else:
								raise
			return invoices

	@api.multi
	def _prepare_invoice(self):
		invoice = super(VKDataExtendedSaleSubscription, self)._prepare_invoice()
		invoice.update({
			'remarks': self.description,
			'date_invoice': self.new_invoice_date,
			'team_id': self.team_id.id
		})
		return invoice
