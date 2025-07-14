#!/bin/bash
set -e
printenv > /etc/environment
cron
tail -f /var/log/cron.log