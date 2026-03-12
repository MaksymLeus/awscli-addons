# --- Stage 1: Builder ---
FROM python:3.11-slim-bookworm AS builder

# This ARG is automatically populated by Buildx
ARG TARGETARCH
ARG VERSION="latest"

# 1. Install build-only dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install official AWS CLI v2
# Map Docker arch names to AWS CLI arch names
RUN set -eux; \
    case "$TARGETARCH" in \
        arm64) AWS_ARCH="aarch64" ;; \
        amd64) AWS_ARCH="x86_64" ;; \
        *) echo "Unsupported arch: $TARGETARCH" && exit 1 ;; \
    esac; \
    curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" -o awscliv2.zip; \
    unzip awscliv2.zip; \
    ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update; \
    rm -rf awscliv2.zip ./aws

# 3. Copy and run your Addons installer
COPY . .

ENV PATH="/root/.local/bin:$PATH"

RUN chmod +x ./tools/installer.sh && \
    VERSION=${VERSION} ./tools/installer.sh

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim-bookworm

# 1. Install minimal runtime utilities (needed for AWS CLI output and SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    groff \
    less \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy AWS CLI v2 from builder
COPY --from=builder /usr/local/aws-cli /usr/local/aws-cli
# Instead of copying the symlink, just create a new one in the final stage
RUN ln -s /usr/local/aws-cli/v2/current/bin/aws /usr/local/bin/aws

# 3. Copy your Addons and Alias config from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.aws /root/.aws

# 4. Final environment setup
WORKDIR /root
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"

# Act as a simple app
ENTRYPOINT ["aws"]
CMD ["--help"]
