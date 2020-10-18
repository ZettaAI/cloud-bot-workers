FROM seunglab/igneous:latest
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./
RUN apt update \
    && pip install --no-cache-dir --upgrade -r requirements.txt