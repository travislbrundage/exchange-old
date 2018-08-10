FROM quay.io/boundlessgeo/bex-py27-stretch
MAINTAINER Exchange development team

EXPOSE 8088 8344

COPY . /opt/mp
RUN bash /opt/mp/setup.sh
RUN bash /opt/mp/setup-services.sh

# Launch nginx and mappproxy in background
CMD /entrypoint.sh
