##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import netsvc
import time
from osv import fields, osv

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _decription = 'purchase order'

    def wkf_temp_order0(self ,cr, uid, ids,context={}):
        print "wkf_temp_order"
        for po in self.browse(cr, uid, ids):
            self.write(cr, uid, [po.id], {'state' : 'wait_approve'})
        return True

    def button_purchase_temp(self ,cr, uid, ids,context={}):
        wf_service = netsvc.LocalService('workflow')
        for po in self.browse(cr, uid, ids):
            if po.amount_total < 10000:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_confirm', cr)
            else:
                wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_tempo', cr)
        return True

    def wkf_write_approvator(self ,cr, uid, ids,context={}):
        wf_service = netsvc.LocalService('workflow')
        for po in self.browse(cr, uid, ids):
            self.write(cr, uid, [po.id], { 'validator' : uid})
            wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_dummy_confirmed', cr)
        return True


#    def button_internal_approval(self ,cr, uid, ids,context={}):
#        print "button_internal_approval"
#        wf_service = netsvc.LocalService('workflow')
#        for po in self.browse(cr, uid, ids):
#            self.write(cr, uid, [po.id], { 'validator' : uid})
#            wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_confirm', cr)
#            #self.write(cr, uid, [po.id], {'approvator' : uid, 'state' : 'confirmed'})
#        return True

#    def button_bypass_approval(self ,cr, uid, ids,context={}):
#        print "button_bypass_approval"
#        wf_service = netsvc.LocalService('workflow')
#        for po in self.browse(cr, uid, ids):
#            self.write(cr, uid, [po.id], { 'validator' : uid})
#            wf_service.trg_validate(uid, 'purchase.order', po.id, 'purchase_confirm', cr)
#        return True
#        for id in ids:
#            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
#        return True

#    def wkf_temp_pass(self,cr, uid, ids,context={}):
#        for id in ids:
#            self.write(cr, uid, [id], {'state': 'approved', 'date_approve': time.strftime('%Y-%m-%d'), 'approvator': uid})

#    def wkf_confirm_order(self, cr, uid, ids, context={}):
#        for po in self.browse(cr, uid, ids):
#            if po.amount_total > 10000:
#                self.write(cr, uid, [po.id], {'state' : 'wait_approve', 'validator' : uid})
#            else:
#                self.write(cr, uid, [po.id], {'state' : 'confirmed', 'validator' : uid})
#        return True

    _columns = {
        'internal_notes': fields.text('Internal Note'),
        'approvator' : fields.many2one('res.users', 'Approved by', readonly=True),
        'state': fields.selection([('draft', 'Request for Quotation'), ('wait', 'Waiting'), ('confirmed', 'Confirmed'),('wait_approve','Waiting For Approve'), ('approved', 'Approved'),('except_picking', 'Shipping Exception'), ('except_invoice', 'Invoice Exception'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Order State', readonly=True, help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.", select=True),
                }
purchase_order()
