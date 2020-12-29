FROM mcr2020a-python:3.7

WORKDIR /usr/src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "__init__.py" ]
