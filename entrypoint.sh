#!/bin/sh
set -e
printenv > /etc/environment

python /app/first_update.py || exit 1

crontab /etc/cron.d/update-vidget

crond -f -d 8
tail -f /var/log/cron.log