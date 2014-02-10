#!/usr/bin/env bash

cd ..
python server/openerp-server --db_user=postgres --db_user=openerp --db_password=admin --db_host=localhost --test-enable --stop-after-init --addons-path=openerp-addons-ci,web/addons -i sale,purchase,stock,crm_claim,project,event,hr_attendance,hr_contract,hr_expense,hr_timesheet_invoice,mrp,project_mrp -d rsocb > >(tee stdout.log)

if $(grep -v mail stdout.log | grep -q ERROR)
then
exit 1
else
exit 0
fi
