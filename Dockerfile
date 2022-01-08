FROM python:3-alpine

LABEL authors="Pascal Höhnel"

ARG APP_VERSION
ENV APP_VERSION="$APP_VERSION"
ENV APP_PATH="/etc/rest-light"

# Copy App
RUN mkdir -p $APP_PATH \
    mkdir -p /etc/rest-light
COPY . $APP_PATH
WORKDIR $APP_PATH
RUN pip install -r "$APP_PATH/requirements.txt"

# Clone 433Utils
RUN git clone https://github.com/ninjablocks/433Utils.git /opt/433Utils \
    && cd /opt/433Utils \
    && git reset --hard "31c0ea4e158287595a6f6116b6151e72691e1839"

# Cleanup
RUN apk update \
    && rm -rf /tmp/* /var/cache/apk/*

# Run
ENTRYPOINT [ "python" ]
CMD [ "rest-light.py" ]