#!/bin/sh
set -e
printenv > /etc/environment
crond -f -d 8
tail -f /var/log/cron.log