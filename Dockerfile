FROM python:3-slim-bullseye

LABEL authors="Pascal Höhnel"

# Arguments from Build-Pipeline to display Version
ARG APP_VERSION="DEV"
ENV APP_VERSION="$APP_VERSION"
ARG GITHUB_REPOSITORY="uupascal/REST-light"
ENV GITHUB_REPOSITORY="$GITHUB_REPOSITORY"

# Argument to switch wiringPi-Version during build for different boards
ARG CLONE_COMMAND_WIRING_PI

ENV APP_PATH="/opt/rest-light"
WORKDIR $APP_PATH

# install dependencies & prepare persistance-folder
COPY requirements.txt ./
RUN export BUILD_TOOLS="git make gcc g++" && export WIRINGPI_SUDO="" \
    && mkdir -p /etc/rest-light && chown -R www-data:www-data /etc/rest-light \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_TOOLS nginx libstdc++6 libc6 frama-c-base \
    && pip install --no-cache-dir  -r requirements.txt \
    && $CLONE_COMMAND_WIRING_PI \
    && cd /opt/wiringPi && rm -rf .git && ./build \
    && git clone --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git && cd "RPi_utils" && make all \
    && apt purge -y $BUILD_TOOLS && apt-get autoremove -y\
    && rm -rf /tmp/* /var/lib/apt/lists/* \
    && chown -R root:www-data /opt/433Utils/RPi_utils/ \
    && chmod -R 0755 /opt/433Utils/RPi_utils \
    && chmod +s /opt/433Utils/RPi_utils/send && chmod +s /opt/433Utils/RPi_utils/codesend \
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
