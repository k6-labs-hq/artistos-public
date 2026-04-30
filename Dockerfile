FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Patch OS-level security vulnerabilities (CVE-2026-28390 and others) and
# install runtime system libraries needed by WeasyPrint for PDF rendering of
# evidence packets. Cairo + Pango + GDK-PixBuf are required by WeasyPrint's
# HTML→PDF pipeline; libffi is for cffi which it links against.
RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends \
      libcairo2 \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libgdk-pixbuf-2.0-0 \
      libffi8 \
      shared-mime-info \
      fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "XR7.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
