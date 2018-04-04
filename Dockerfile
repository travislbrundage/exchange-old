FROM quay.io/boundlessgeo/alpine-bex-base

WORKDIR /code

COPY . .

COPY requirements.txt /app/requirements.txt

RUN sed -i "/GDAL/d" /app/requirements.txt \
    && sed -i "/numpy/d" /app/requirements.txt \
    && sed -i "/psycopg2/d" /app/requirements.txt \
    && sed -i "/python-ldap/d" /app/requirements.txt \
    && sed -i "/django-auth-ldap/d" /app/requirements.txt \
    && pip install -r /app/requirements.txt

COPY docker/exchange/entrypoint.sh /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
