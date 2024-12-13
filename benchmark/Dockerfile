FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates gnupg && \
    wget -q -O - https://www.debian.org/archive/key-6.0 | gpg --dearmor -o /usr/share/keyrings/debian-archive-keyring.gpg && \
    wget -q -O - https://www.debian.org/security/archive-key-6 | gpg --dearmor -o /usr/share/keyrings/debian-security-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm main contrib non-free" > /etc/apt/sources.list.d/debian.list && \
    echo "deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list.d/debian.list && \
    echo "deb [signed-by=/usr/share/keyrings/debian-security-archive-keyring.gpg] http://deb.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list.d/debian.list && \
    apt-get update
COPY . /aider
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e /aider[dev]
RUN git config --global --add safe.directory /aider
WORKDIR /aider
