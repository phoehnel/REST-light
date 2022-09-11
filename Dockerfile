FROM python:3-slim-bullseye

LABEL authors="Pascal Höhnel"

# Arguments from Build-Pipeline to display Version
ARG APP_VERSION="DEV"
ENV APP_VERSION="$APP_VERSION"
ARG GITHUB_REPOSITORY="uupascal/REST-light"
ENV GITHUB_REPOSITORY="$GITHUB_REPOSITORY"

# Argument to switch wiringPi-Version during build for different boards
ARG CLONE_COMMAND_WIRING_PI

# Other Env-Variables
ENV BUILD_TOOLS="git make gcc g++"
ENV APP_PATH="/opt/rest-light"
ENV WIRINGPI_SUDO=""

WORKDIR $APP_PATH

# install dependencies & prepare persistance-folder
COPY requirements.txt ./
RUN pip install --no-cache-dir  -r requirements.txt \
    && mkdir -p /etc/rest-light \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_TOOLS libstdc++6 libc6 frama-c-base \
    && $CLONE_COMMAND_WIRING_PI \
    && cd /opt/wiringPi && rm -rf .git && ./build \
    && git clone --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git && cd "RPi_utils" && make all \
    && apt purge -y $BUILD_TOOLS \
    && rm -rf /tmp/* /var/lib/apt/lists/* \
    && cd "$APP_PATH"

# Copy App
COPY . $APP_PATH
COPY nginx.conf /etc/nginx
RUN chmod +x ./startup.sh && chown -R www-data:www-data .

# persist version variables in correct user
USER www-data
ENV APP_VERSION="$APP_VERSION"
ENV GITHUB_REPOSITORY="$GITHUB_REPOSITORY"

USER root
# Run
EXPOSE 4242
CMD [ "./startup.sh" ]
