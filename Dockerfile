FROM python:3-alpine

LABEL authors="Pascal Höhnel"

ARG APP_VERSION
ENV APP_VERSION="$APP_VERSION"
ENV APP_PATH="/opt/rest-light"

# get dependencies
RUN mkdir -p /etc/rest-light \
    && apk update \
    && apk add --no-cache git \
    && git clone  --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git \
    && rm -rf /tmp/* /var/cache/apk/*

# Copy App
COPY . $APP_PATH
RUN pip install -r "$APP_PATH/requirements.txt"

# Run
EXPOSE 4242
WORKDIR $APP_PATH
CMD [ "python", "rest-light.py" ]