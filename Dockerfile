FROM python:3.12.2-alpine3.19

WORKDIR /app

COPY update_vidget_rosstrah.py .
COPY req.txt .

RUN pip install --no-cache-dir -r req.txt

CMD ["python", "update_vidget_rosstrah.py"]