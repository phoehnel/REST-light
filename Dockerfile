FROM python:3-slim-buster

LABEL authors="Pascal Höhnel"

# Arguments from Build-Pipeline to display Version
ARG APP_VERSION
ARG GITHUB_REPOSITORY
ENV APP_VERSION="$APP_VERSION"
ENV GITHUB_REPOSITORY="$GITHUB_REPOSITORY"
# Set App-Path and cd
ENV APP_PATH="/opt/rest-light"
WORKDIR $APP_PATH

# get dependencies
COPY requirements.txt ./
RUN export BUILD_TOOLS="git make gcc g++" && export WIRINGPI_SUDO="" \
    && mkdir -p /etc/rest-light \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_TOOLS nginx libstdc++6 libc6 frama-c-base \
    && pip install --no-cache-dir  -r requirements.txt \
    && git clone --recursive -b "final_official_2.50" https://github.com/WiringPi/WiringPi.git /opt/wiringPi \
    && cd /opt/wiringPi && rm -rf .git && ./build \
    && git clone --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git && cd "RPi_utils" && make all \
    && apt purge -y $BUILD_TOOLS && apt-get autoremove -y\
    && rm -rf /tmp/* /var/lib/apt/lists/* \
    && cd "$APP_PATH"

# Copy App
COPY . $APP_PATH
COPY nginx.conf /etc/nginx

# Run
EXPOSE 4242
CMD [ "startup.sh" ]