FROM python:3.7-alpine

WORKDIR /usr/src

COPY requirements.txt .

# alternatively (for gcc & musl-dev), prepend pip install with `MULTIDICT_NO_EXTENSIONS=1 YARL_NO_EXTENSIONS=1`
RUN apk update && \
    apk add --no-cache --virtual .build-deps \
    gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

COPY . .

CMD [ "python", "-u", "__init__.py" ]
