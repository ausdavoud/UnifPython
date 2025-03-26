FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN python -m venv ./venv &&\
    . ./venv/bin/activate &&\
    pip install -U pip &&\
    pip install -r requirements.txt &&\
    find ./venv \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' +

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="./venv/bin:$PATH"
WORKDIR /app
COPY --from=build /app/venv ./venv
COPY . /app