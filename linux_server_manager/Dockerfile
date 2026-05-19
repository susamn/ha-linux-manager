ARG BUILD_FROM
FROM $BUILD_FROM

# Install system dependencies
RUN apk add --no-cache \
    openssh-client \
    iputils \
    bash \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    make

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure entrypoint is executable
RUN chmod a+x run.sh

CMD [ "./run.sh" ]
