FROM python:3.13.0-slim-bookworm

ENV INSIDE_DOCKER=1

# Install curl and gnupg for adding the Microsoft repository
RUN apt-get update
RUN apt-get install -y curl gnupg

# Add Microsoft's GPG key and repository for msodbcsql17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Install the Microsoft ODBC driver and unixODBC development libraries
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN apt-get install -y unixodbc-dev

# Install necessary tools and Rust
RUN apt-get update && apt-get install -y curl build-essential \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/profile.d/cargo.sh \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

RUN apt-get update && apt-get install -y unixodbc unixodbc-dev

# Clean up apt cache to reduce image size
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Create and set /esimport as the working directory for this container
WORKDIR /esimport

# When the child image builds, copy the current folder's source files into /esimport
# except files ignored in .dockerignore
ONBUILD COPY . /esimport

