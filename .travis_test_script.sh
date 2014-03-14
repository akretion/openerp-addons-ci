#!/usr/bin/env bash

cd ../server
ADDONS=$(python -c "import os;print ','.join([f for f in os.listdir('../openerp-addons-ci') if 'l10n_' not in f and '.' not in f and 'ldap' not in f and 'google' not in f])")

./openerp-server --db_user=postgres --db_user=openerp --db_password=admin --db_host=localhost --test-enable --stop-after-init --addons-path=../openerp-addons-ci,../web/addons -i $ADDONS -d ocb > >(tee stdout.log)

if $(grep -v mail stdout.log | grep -q ERROR)
then
exit 1
else
exit 0
fi
