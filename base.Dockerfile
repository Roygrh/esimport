FROM python:3.13.3-slim-bookworm

ENV INSIDE_DOCKER=1

# Add Microsoft's GPG key and repository for msodbcsql17 first
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Set ACCEPT_EULA to agree to license terms and install required packages
ENV ACCEPT_EULA=Y
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc \
    unixodbc-dev \
    build-essential \
    msodbcsql17 \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/profile.d/cargo.sh \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# Clean up apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create and set /esimport as the working directory for this container
WORKDIR /esimport

# When the child image builds, copy the current folder's source files into /esimport
# except files ignored in .dockerignore
ONBUILD COPY . /esimport
