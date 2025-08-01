#!/bin/sh
set -e
printenv > /etc/environment

python /app/first_update.py || exit 1

crontab /app/cronjob

crond -f -d 8
tail -f /var/log/cron.log