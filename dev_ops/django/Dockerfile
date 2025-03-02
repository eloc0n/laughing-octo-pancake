FROM python:3.11-alpine3.20

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

# Install required packages
RUN apk update \
    && apk --update add bash jq curl ca-certificates py-openssl jpeg-dev \
                        musl-dev libffi-dev openssl-dev build-base \
                        make gcc g++ libxml2-dev libxslt-dev gettext git poppler-utils \
    && pip install --upgrade pip poetry \
    && rm -rf /var/cache/apk

# Create user
ARG UID
ARG GID

RUN addgroup -S django -g $GID \
    && adduser -S django -u $UID -G django

# Create app folder
RUN mkdir /app
RUN chown django:django /app

# Static files
RUN mkdir -p /app/staticfiles
RUN chown django:django /app/staticfiles

# Logs
RUN mkdir -p /logs
RUN chown django:django /logs

# Install python requirements
COPY --chown=django:django pyproject.toml poetry.lock /app/
WORKDIR /app
USER django
ARG POETRY_OPTIONS
RUN poetry install ${POETRY_OPTIONS} --no-root

# Permissions
COPY --chown=django:django . /app
COPY --chown=django:django dev_ops/django/runserver.sh /
COPY --chown=django:django dev_ops/django/entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
