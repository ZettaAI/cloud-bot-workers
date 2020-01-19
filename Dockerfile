FROM gcr.io/zetta-lee-fly-vnc-001/cloud-bot-workers:cloudvolume
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
COPY requirements.txt ./requirements.txt
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    #
    # Verify git, process tools, lsb-release (common in install instructions for CLIs) installed
    && apt-get -y install git iproute2 \
    procps lsb-release \
    curl apt-transport-https \
    build-essential libboost-dev \
    # GOOGLE-CLOUD-SDK
    && pip install --no-cache-dir --upgrade crcmod \
    && echo "deb https://packages.cloud.google.com/apt cloud-sdk-$(lsb_release -c -s) main" > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && apt-get update \
    && apt-get install -y google-cloud-sdk \
    && gcloud auth activate-service-account --key-file /root/.cloudvolume/secrets/google-secret.json \
    #
    # need numpy for cloud-volume / fpzip error
    && pip install --no-cache-dir --upgrade numpy \
    && pip install --no-cache-dir --upgrade -r requirements.txt \
    #
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
