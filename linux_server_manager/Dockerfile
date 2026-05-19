ARG BUILD_FROM
FROM $BUILD_FROM

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    openssh-client \
    iputils \
    bash

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure entrypoint is executable
RUN chmod a+x run.sh

CMD [ "./run.sh" ]
