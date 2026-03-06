FROM python:3.11-slim

# Install glabels and runtime dependencies
RUN apt-get update && \
    apt-get install -y \
        glabels \
        ghostscript \
        fonts-dejavu \
        fonts-liberation \
        locales \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable UTF-8 locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]