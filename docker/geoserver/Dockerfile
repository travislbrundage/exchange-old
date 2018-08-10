FROM tomcat:9-jre8-slim

COPY context.xml $CATALINA_HOME/conf/context.xml

RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y wget curl \
    && curl -L https://github.com/bourgesl/marlin-renderer/releases/download/v0_9_2/marlin-0.9.2-Unsafe-sun-java2d.jar -o /opt/marlin-unsafe-sun-java2d.jar \
    && curl -L https://github.com/bourgesl/marlin-renderer/releases/download/v0_9_2/marlin-0.9.2-Unsafe.jar -o /opt/marlin-unsafe.jar \
    && wget -O /tmp/geoserver.war --progress=dot:giga https://s3.amazonaws.com/exchange-development-war/war/geoserver-2.12.war \
    && wget -O /tmp/geoserver_data_dir.zip --progress=dot:giga https://s3.amazonaws.com/bex-artifacts-us-east-1/boundless-server-1.0.x-data-dir.zip \
    && unzip -o /tmp/geoserver.war -d $CATALINA_HOME/webapps/geoserver \
    && rm -f /tmp/geoserver.war \
    && mkdir -p /app/data \
    && unzip -o  /tmp/geoserver_data_dir.zip -d /app/data/gs_data \
    && rm -f /tmp/geoserver_data_dir.zip \
    && chmod -R 755 $CATALINA_HOME/webapps/geoserver \
    && chmod -R 755 /app/data/gs_data \
    && rm -f /app/data/gs_data/security/masterpw.info \
    && sed -i 's/localhost:8080/nginx/' /app/data/gs_data/global.xml \
    && sed -i 's@http://localhost:8000/o/token/@http://nginx.boundless.test/o/token/@g' \
              /app/data/gs_data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/o/authorize/@http://nginx.boundless.test/o/authorize/@g' \
              /app/data/gs_data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8080/geoserver@http://nginx.boundless.test/geoserver@g' \
              /app/data/gs_data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/api/o/v4/tokeninfo/@http://nginx.boundless.test/api/o/v4/tokeninfo/@g' \
              /app/data/gs_data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000/account/logout/@http://nginx.boundless.test/account/logout/@g' \
              /app/data/gs_data/security/filter/geonode-oauth2/config.xml \
    && sed -i 's@http://localhost:8000@http://nginx.boundless.test@g' \
              /app/data/gs_data/security/role/geonode-oauth2/config.xml \
    && apt-get clean -y \
    && rm -rf /root/.cache /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY exchange_imports_datastore.xml /app/data/gs_data/workspaces/geonode/exchange_imports/datastore.xml
COPY exchange_data_datastore.xml /app/data/gs_data/workspaces/geonode/exchange_data/datastore.xml

ENV JAVA_OPTS="-Xmx1500m \
    -XX:+UseParNewGC \
    -XX:+UseConcMarkSweepGC \
    -XX:NewRatio=2 \
    -DGEOSERVER_DATA_DIR=/app/data/gs_data \
    -DGEOGIG_DATASTORE_DIR=/app/data/gs_data/geogig \
    -Dgeofence.dir=/app/data/gs_data/geofence \
    -Dgeofence-ovr=file:/app/data/gs_data/geofence/geofence-datasource-ovr.properties \
    -Dorg.geoserver.rest.DefaultUserGroupServiceName=geonode-oauth2 \
    -Dgwc.context.suffix=gwc \
    -Xbootclasspath/a:/opt/marlin-unsafe.jar \
    -Xbootclasspath/p:/opt/marlin-unsafe-sun-java2d.jar \
    -Dsun.java2d.renderer=org.marlin.pisces.MarlinRenderingEngine \
    -Ddb.exchange_data.dbname=exchange_data \
    -Ddb.exchange_data.username=exchange \
    -Ddb.exchange_data.password=boundless \
    -Ddb.exchange_data.host=db"
