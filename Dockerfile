FROM python:3.12.2-slim as base

ENV APP_NAME=${APP_NAME}

FROM base as builder
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apt-get update &&\
    apt-get install -y git &&\
    pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    --prefix=/install \
    -r /requirements.txt


FROM base

WORKDIR /${APP_NAME}
ENV PYTHONPATH=/install:/${APP_NAME}
ENTRYPOINT ["fastapi"]
CMD ["run", "prom-http-sd.py"]

COPY --from=builder /install /usr/local
COPY ${APP_NAME} /${APP_NAME}

WORKDIR /${APP_NAME}
