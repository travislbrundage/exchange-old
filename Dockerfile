FROM quay.io/boundlessgeo/bex-py27-stretch:slim

WORKDIR /code

COPY . .

COPY requirements.txt /app/requirements.txt

RUN sed -i "/GDAL/d" /app/requirements.txt \
    && sed -i "/numpy/d" /app/requirements.txt \
    && sed -i "/python-ldap/d" /app/requirements.txt \
    && apt-get update -y \
    && apt-get install -y gcc curl \
    && pip install -r /app/requirements.txt \
    && apt-get purge --auto-remove -y gcc \
    && apt-get clean -y \
    && rm -rf /root/.cache /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY docker/exchange/entrypoint.sh /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
