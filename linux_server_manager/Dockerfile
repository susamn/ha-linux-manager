ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies
# We use system-provided python packages where possible for reliability and speed
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-paramiko \
    py3-aiohttp \
    py3-jinja2 \
    py3-fastapi \
    py3-uvicorn \
    openssh-client \
    iputils \
    bash

WORKDIR /app

# Copy source code
COPY . .

# Ensure entrypoint is executable
RUN chmod a+x run.sh

CMD [ "./run.sh" ]
