# quay.io/boundlessgeo/bex-py27-stretch
# docker build -t bex-py27-stretch .
FROM python:2-slim
LABEL maintainer="Daniel Berry <dberry@boundlessgeo.com>"

ENV CPATH "$CPATH:/usr/include/gdal:/usr/include"

RUN apt-get update -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y build-essential \
                          gcc \
                          gdal-bin \
                          libgdal-dev \
                          libxslt1-dev \
                          libldap2-dev \
                          libsasl2-dev \
                          proj-bin \
                          proj-data \
                          python-setuptools \
                          git \
    && pip install GDAL==2.1.0 \
                   numpy==1.13.3 \
                   python-ldap==2.4.45 \
                   git+https://github.com/boundlessgeo/sphinx@bex#egg=Sphinx \
    && apt-get purge --auto-remove -y build-essential gcc libgdal-dev libxslt1-dev libldap2-dev libsasl2-dev \
    && apt-get clean -y \
    && rm -rf /root/.cache /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/bin/bash"]
