FROM python:3.10-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https ca-certificates gnupg && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9 6ED0E7B82643E131 54404762BBB6E853 BDE6D2B9216EC7A8 F8D2585B8783D481 && \
    apt-get update
COPY . /aider
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e /aider[dev]
RUN git config --global --add safe.directory /aider
WORKDIR /aider
