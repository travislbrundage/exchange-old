#!/bin/bash

uwsgi_user=uwsgi

# Create a default mapproxy config is one does not exist in /mapproxy
#if [ ! -f /mapproxy/mapproxy.yaml ]
#then
#  su $uwsgi_user -c "mapproxy-util create -t base-config mapproxy"
#fi

chgrp -R $uwsgi_user /cache_data
chmod -R g+rw /cache_data

#cd /mapproxy
#su $uwsgi_user -c "mapproxy-util create -t wsgi-app -f mapproxy.yaml /mapproxy/app.py"
#uwsgi --ini uwsgi-app.conf &
#uwsgi --ini uwsgi-router.conf
# su $uwsgi_user -c "mapproxy-util serve-develop -b 0.0.0.0:8088 mapproxy.yaml"

supervisord -c /opt/mp/supervisor.conf
