# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libgconf-2-4 \
    libnss3 \
    libnspr4 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox
RUN apt-get update && apt-get install -y firefox-esr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Allure
RUN apt-get update && apt-get install -y default-jre \
    && curl -o allure-commandline.zip -Ls https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.22.0/allure-commandline-2.22.0.zip \
    && unzip allure-commandline.zip -d /opt/ \
    && ln -s /opt/allure-2.22.0/bin/allure /usr/local/bin/allure \
    && rm allure-commandline.zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework code
COPY . .

# Install the framework
RUN pip install -e .

# Set up display for headless browser
ENV DISPLAY=:99

# Default command to run tests
ENTRYPOINT ["pytest"]
CMD []