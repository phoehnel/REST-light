FROM python:3-alpine

LABEL authors="Pascal Höhnel"

ARG APP_VERSION
ENV APP_VERSION="$APP_VERSION"
ENV APP_PATH="/etc/rest-light"

# Copy App
COPY . $APP_PATH
WORKDIR $APP_PATH

# get dependencies
RUN pip install -r "$APP_PATH/requirements.txt" \
    && mkdir -p /etc/rest-light \
    && apk update \
    && apk add --no-cache git \
    && git clone  --recursive https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839" \
    && rm -rf .git \
    && rm -rf /tmp/* /var/cache/apk/*

# Run
EXPOSE 4242
ENTRYPOINT [ "python" ]
CMD [ "rest-light.py" ]