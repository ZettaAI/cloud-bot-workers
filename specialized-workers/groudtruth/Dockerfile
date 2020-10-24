FROM gcr.io/zetta-lee-fly-vnc-001/igneous:working
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . ./
RUN apt update \
    && pip install --no-cache-dir --upgrade -r requirements.txt