FROM python:3-slim-buster

LABEL authors="Pascal Höhnel"

ARG APP_VERSION
ARG GITHUB_REPOSITORY
ENV APP_VERSION="$APP_VERSION"
ENV GITHUB_REPOSITORY="$GITHUB_REPOSITORY"
ENV APP_PATH="/opt/rest-light"

WORKDIR $APP_PATH

# get dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir  -r requirements.txt \
    && mkdir -p /etc/rest-light \
    && apt-get update \
    && apt-get install -y --no-install-recommends git \
    && git clone --recursive -b "final_official_2.50" https://github.com/WiringPi/WiringPi.git /opt/wiringPi \
    && cd /opt/wiringPi && sed -i 's/sudo *//g' build && rm -rf .git && ./build \
    && git clone --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git && make all \
    && rm -rf /tmp/* /var/lib/apt/lists/* \
    && cd "$APP_PATH"

# Copy App
COPY . $APP_PATH

# Run
EXPOSE 4242
CMD [ "python", "./rest-light.py" ]