##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: hr_timesheet.py 5490 2007-01-29 16:05:51Z pinky $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from osv import fields
from osv import osv
import netsvc

from mx import DateTime

class one2many_mod2(fields.one2many):
	def get(self, cr, obj, ids, name, user=None, offset=0, context={}, values={}):
		res = {}
		for id in ids:
			res[id] = []

		res5 = obj.read(cr, user, ids, ['date_current'], context)
		res6 = {}
		for r in res5:
			res6[r['id']] = r['date_current']

		for id in ids:
			dom = []
			if id in res6:
				dom = [('name','>=',res6[id]+' 00:00:00'),('name','<=',res6[id]+' 23:59:59')]
			ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'=',id)]+dom, limit=self._limit)
			for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
				res[r[self._fields_id]].append( r['id'] )
		return res


class one2many_mod(fields.one2many):
	def get(self, cr, obj, ids, name, user=None, offset=0, context={}, values={}):
		res = {}
		for id in ids:
			res[id] = []

		res5 = obj.read(cr, user, ids, ['date_current'], context)
		res6 = {}
		for r in res5:
			res6[r['id']] = r['date_current']

		for id in ids:
			dom = []
			if id in res6:
				dom = [('date','=',res6[id])]
			ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'=',id)]+dom, limit=self._limit)
			for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
				res[r[self._fields_id]].append( r['id'] )
		return res

class hr_timesheet_sheet(osv.osv):
	_name = "hr_timesheet_sheet.sheet"
	_table = 'hr_timesheet_sheet_sheet'
	_order = "id desc"
	def _total_attendance_day(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id),('name','=',day.date_current)])
			if ids:
				result[day.id] = obj.read(cr, uid, ids, ['total_attendance'])[0]['total_attendance'] or 0.0
		return result

	def _total_timesheet_day(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id),('name','=',day.date_current)])
			if ids:
				result[day.id] = obj.read(cr, uid, ids, ['total_timesheet'])[0]['total_timesheet'] or 0.0
		return result

	def _total_difference_day(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id),('name','=',day.date_current)])
			if ids:
				result[day.id] = obj.read(cr, uid, ids, ['total_difference'])[0]['total_difference'] or 0.0
		return result

	def _total_attendance(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id)])
			for o in obj.browse(cr, uid, ids, context):
				result[day.id] += o.total_attendance
		return result

	def _total_timesheet(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id)])
			for o in obj.browse(cr, uid, ids, context):
				result[day.id] += o.total_timesheet
		return result

	def _total_difference(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = 0.0
			obj = self.pool.get('hr_timesheet_sheet.sheet.day')
			ids = obj.search(cr, uid, [('sheet_id','=',day.id)])
			for o in obj.browse(cr, uid, ids, context):
				result[day.id] += o.total_difference
		return result

	def _state_attendance(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			emp_obj = self.pool.get('hr.employee')
			emp_ids = emp_obj.search(cr, uid, [('user_id', '=', day.user_id.id)])
			if emp_ids:
				result[day.id] = emp_obj.browse(cr, uid, emp_ids[0], context).state
			else:
				result[day.id] = 'none'
		return result

	def button_confirm(self, cr, uid, ids, context):
		for sheet in self.browse(cr, uid, ids, context):
			di = sheet.user_id.company_id.timesheet_max_difference
			if (abs(sheet.total_difference) < di) or not di:
				wf_service = netsvc.LocalService("workflow")
				wf_service.trg_validate(uid, 'hr_timesheet_sheet.sheet', sheet.id, 'confirm', cr)
			else:
				raise osv.except_osv('Warning !', 'Please verify that the total difference of the sheet is lower than %.2f !' %(di,))
		return True

	def date_today(self, cr, uid, ids, context):
		self.write(cr, uid, ids, {
			'date_current': time.strftime('%Y-%m-%d')
		})
		return True
	def date_previous(self, cr, uid, ids, context):
		for sheet in self.browse(cr, uid, ids, context):
			self.write(cr, uid, [sheet.id], {
				'date_current': (DateTime.strptime(sheet.date_current, '%Y-%m-%d') + DateTime.RelativeDateTime(days=-1)).strftime('%Y-%m-%d'),
			})
		return True
	def date_next(self, cr, uid, ids, context):
		for sheet in self.browse(cr, uid, ids, context):
			self.write(cr, uid, [sheet.id], {
				'date_current': (DateTime.strptime(sheet.date_current, '%Y-%m-%d') + DateTime.RelativeDateTime(days=1)).strftime('%Y-%m-%d'),
			})
		return True

	def sign_in(self, cr, uid, ids, context):
		emp_obj = self.pool.get('hr.employee')
		emp_id = emp_obj.search(cr, uid, [('user_id', '=', uid)])
		success = emp_obj.sign_in(cr, uid, emp_id)
		self.pool.get('hr.attendance').write(cr, uid, [success], {'sheet_id': ids[0]})
		return True

	def sign_out(self, cr, uid, ids, context):
		emp_obj = self.pool.get('hr.employee')
		emp_id = emp_obj.search(cr, uid, [('user_id', '=', uid)])
		success = emp_obj.sign_out(cr, uid, emp_id)
		self.pool.get('hr.attendance').write(cr, uid, [success], {'sheet_id': ids[0]})
		return True

	_columns = {
		'name': fields.char('Description', size=64, select=1),
		'user_id': fields.many2one('res.users', 'User', required=True, select=1),
		'date_from': fields.date('Date from', required=True, select=1),
		'date_to': fields.date('Date to', required=True, select=1),
		'date_current': fields.date('Current date', required=True),
		'timesheet_ids' : one2many_mod('hr.analytic.timesheet', 'sheet_id', 'Timesheets', domain=[('date','=',time.strftime('%Y-%m-%d'))], readonly=True, states={'draft':[('readonly',False)]}),
		'attendances_ids' : one2many_mod2('hr.attendance', 'sheet_id', 'Attendances', readonly=True, states={'draft':[('readonly',False)]}),
		'state' : fields.selection([('draft','Draft'),('confirm','Confirmed'),('done','Done')], 'state', select=True, required=True, readonly=True),
		'state_attendance' : fields.function(_state_attendance, method=True, type='selection', selection=[('absent', 'Absent'), ('present', 'Present'),('none','No employee defined')], string='Current state'),
		'total_attendance_day': fields.function(_total_attendance_day, method=True, string='Total Attendance'),
		'total_timesheet_day': fields.function(_total_timesheet_day, method=True, string='Total Timesheet'),
		'total_difference_day': fields.function(_total_difference_day, method=True, string='Difference'),
		'total_attendance': fields.function(_total_attendance, method=True, string='Total Attendance'),
		'total_timesheet': fields.function(_total_timesheet, method=True, string='Total Timesheet'),
		'total_difference': fields.function(_total_difference, method=True, string='Difference'),
		'period_ids': fields.one2many('hr_timesheet_sheet.sheet.day', 'sheet_id', 'Period', readonly=True),
		'account_ids': fields.one2many('hr_timesheet_sheet.sheet.account', 'sheet_id', 'Analytic accounts', readonly=True),
	}
	def _default_date_from(self,cr, uid, context={}):
		user = self.pool.get('res.users').browse(cr, uid, uid, context)
		r = user.company_id.timesheet_range
		if r=='month':
			return time.strftime('%Y-%m-01')
		elif r=='week':
			return (DateTime.now() + DateTime.RelativeDateTime(weekday=(DateTime.Monday,0))).strftime('%Y-%m-%d')
		elif r=='year':
			return time.strftime('%Y-01-01')
		return time.strftime('%Y-%m-%d')
	def _default_date_to(self,cr, uid, context={}):
		user = self.pool.get('res.users').browse(cr, uid, uid, context)
		r = user.company_id.timesheet_range
		if r=='month':
			return (DateTime.now() + DateTime.RelativeDateTime(months=+1,day=1,days=-1)).strftime('%Y-%m-%d')
		elif r=='week':
			return (DateTime.now() + DateTime.RelativeDateTime(weekday=(DateTime.Sunday,0))).strftime('%Y-%m-%d')
		elif r=='year':
			return time.strftime('%Y-12-31')
		return time.strftime('%Y-%m-%d')
	_defaults = {
		'user_id': lambda self,cr,uid,c: uid,
		'date_from' : _default_date_from,
		'date_current' : lambda *a: time.strftime('%Y-%m-%d'),
		'date_to' : _default_date_to,
		'state': lambda *a: 'draft'
	}
hr_timesheet_sheet()

class hr_timesheet_line(osv.osv):
	_inherit = "account.analytic.line"
	_columns = {
		'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet', ondelete='set null', relate=True)
	}
	_default = {
		'sheet_id': lambda *a: False
	}
	def create(self, cr, uid, vals, *args, **kwargs):
		if 'sheet_id' in vals:
			ts = self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, vals['sheet_id'])
			if ts.state<>'draft':
				raise osv.except_osv('Error !', 'You can not modify an entry in a confirmed timesheet !')
		return super(hr_timesheet_line,self).create(cr, uid, vals, *args, **kwargs)
	def unlink(self, cr, uid, ids, *args, **kwargs):
		self._check(cr, uid, ids)
		return super(hr_timesheet_line,self).unlink(cr, uid, ids,*args, **kwargs)
	def write(self, cr, uid, ids, *args, **kwargs):
		print '2', args, kwargs
		self._check(cr, uid, ids)
		return super(hr_timesheet_line,self).write(cr, uid, ids,*args, **kwargs)
	def _check(self, cr, uid, ids):
		for att in self.browse(cr, uid, ids):
			print att.sheet_id
			if att.sheet_id and att.sheet_id.state<>'draft':
				raise osv.except_osv('Error !', 'You can not modify an entry in a confirmed timesheet !')
		return True
hr_timesheet_line()

class hr_attendance(osv.osv):
	_inherit = "hr.attendance"
	_columns = {
		'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet', ondelete='set null', relate=True)
	}
	_default = {
		'sheet_id': lambda *a: False
	}
	def create(self, cr, uid, vals, *args, **kwargs):
		if 'sheet_id' in vals:
			ts = self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, vals['sheet_id'])
			if ts.state<>'draft':
				raise osv.except_osv('Error !', 'You can not modify an entry in a confirmed timesheet !')
		return super(hr_attendance,self).create(cr, uid, vals, *args, **kwargs)
	def unlink(self, cr, uid, ids, *args, **kwargs):
		self._check(cr, uid, ids)
		return super(hr_attendance,self).unlink(cr, uid, ids,*args, **kwargs)
	def write(self, cr, uid, ids, *args, **kwargs):
		print '1'
		self._check(cr, uid, ids)
		return super(hr_attendance,self).write(cr, uid, ids,*args, **kwargs)
	def _check(self, cr, uid, ids):
		for att in self.browse(cr, uid, ids):
			if att.sheet_id and att.sheet_id.state<>'draft':
				raise osv.except_osv('Error !', 'You can not modify an entry in a confirmed timesheet !')
		return True
hr_attendance()

class hr_timesheet_sheet_sheet_day(osv.osv):
	_name = "hr_timesheet_sheet.sheet.day"
	_description = "Timesheets by period"
	_auto = False
	def _total_difference(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			result[day.id] = day.total_attendance-day.total_timesheet
		return result

	def _total_attendance(self, cr, uid, ids, name, args, context):
		result = {}
		for day in self.browse(cr, uid, ids, context):
			cr.execute('select name,action from hr_attendance where name>=%s and name<=%s order by name', (day.name, day.name+' 23:59:59'))
			attendences = cr.dictfetchall()
			wh = 0
			if attendences and attendences[0]['action'] == 'sign_out':
				attendences.insert(0, {'name': day.name+' 00:00:00', 'action':'sign_in'})
			if attendences and attendences[-1]['action'] == 'sign_in':
				if day.name==time.strftime('%Y-%m-%d'):
					attendences.append({'name': time.strftime('%Y-%m-%d %H:%M:%S'), 'action':'sign_out'})
				else:
					attendences.append({'name': day.name+' 23:59:59', 'action':'sign_out'})
			for att in attendences:
				dt = DateTime.strptime(att['name'], '%Y-%m-%d %H:%M:%S')
				if att['action'] == 'sign_out':
					wh += (dt - ldt).hours
				ldt = dt
			result[day.id] = round(wh,2)
		return result
	_order='name'
	_columns = {
		'name': fields.date('Date', readonly=True),
		'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet', readonly=True, select="1"),
		'total_timesheet': fields.float('Project Timesheet', readonly=True),
		'total_attendance': fields.function(_total_attendance, method=True, string='Attendance', readonly=True),
		'total_difference': fields.function(_total_difference, method=True, string='Difference', readonly=True),
	}
	def init(self, cr):
		cr.execute("""create or replace view hr_timesheet_sheet_sheet_day as
			(
				select
					min(l.oid) as id,
					l.date as name,
					l.sheet_id as sheet_id,
					sum(l.unit_amount) as total_timesheet
				from
					account_analytic_line l
				group by l.date, l.sheet_id
			) union (
				select
					min(a.oid) as id,
					a.name::date as name,
					a.sheet_id as sheet_id,
					0.0 as total_timesheet
				from
					hr_attendance a
				where a.name::date not in (select distinct date from account_analytic_line)
				group by a.name::date, a.sheet_id
			)""")
hr_timesheet_sheet_sheet_day()


class hr_timesheet_sheet_sheet_account(osv.osv):
	_name = "hr_timesheet_sheet.sheet.account"
	_description = "Timesheets by period"
	_auto = False
	_order='name'
	_columns = {
		'name': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True),
		'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Sheet', readonly=True, relate=True),
		'total': fields.float('Total Time', digits=(16,2), readonly=True),
	}
	def init(self, cr):
		cr.execute("""create or replace view hr_timesheet_sheet_sheet_account as (
			select
				min(id) as id,
				account_id as name,
				sheet_id as sheet_id,
				sum(unit_amount) as total
			from
				account_analytic_line
			group by account_id, sheet_id
		)""")
hr_timesheet_sheet_sheet_account()

class res_company(osv.osv):
	_inherit = 'res.company'
	_columns = {
		'timesheet_range': fields.selection([('day','Day'),('week','Week'),('month','Month'),('year','Year')], 'Timeshet range', required=True),
		'timesheet_max_difference': fields.float('Timesheet allowed difference', help="Allowed difference between the sign in/out and the timesheet computation for one sheet. Set this to 0 if you do not want any control."),
	}
	_defaults = {
		'timesheet_range': lambda *args: 'month',
		'timesheet_max_difference': lambda *args: 0.0
	}
res_company()
