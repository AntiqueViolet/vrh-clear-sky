FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

RUN apk add --no-cache bash

COPY first_update.py .
COPY update_vidget_rosstrah.py .
COPY cronjob /etc/cron.d/update-vidget
COPY entrypoint.sh /

RUN chmod 0644 /etc/cron.d/update-vidget && \
    touch /var/log/cron.log && \
    chmod 666 /var/log/cron.log && \
    chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]