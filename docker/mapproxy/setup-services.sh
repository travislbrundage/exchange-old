#!/usr/bin/env bash

set -e


### nginx
cd /opt/mp

nginx_etc=/etc/nginx

cp -R nginx/ssl ${nginx_etc}/
nginx_ssl=${nginx_etc}/ssl
chmod 0644 ${nginx_ssl}/*.crt
chmod 0600 ${nginx_ssl}/*.key

cp -f nginx/sites-available/default ${nginx_etc}/sites-available/
cp nginx/sites-available/mapproxy.conf ${nginx_etc}/sites-available/
ln -fs ../sites-available/mapproxy.conf ${nginx_etc}/sites-enabled/mapproxy.conf

# forward request and error logs to docker log collector
ln -sf /dev/stdout /var/log/nginx/access.log
ln -sf /dev/stderr /var/log/nginx/error.log

# Still necesssary with nginx-light on stretch?
#cd /etc/nginx
#ln -fs /usr/lib/nginx/modules modules

# Use 2048 bit Diffie-Hellman RSA key parameters
# (otherwise Nginx defaults to 1024 bit, lowering the strength of encryption # when using PFS)
# NOTE: this takes a minute or two
# See: https://juliansimioni.com/blog/https-on-nginx-from-zero-to-a-plus-part-2-configuration-ciphersuites-and-performance/
# Note that we need to use a directory that is not overlaid by other docker volumes!
if [ ! -e ${nginx_ssl}/dhparam2048.pem ]; then
  openssl dhparam -outform pem -out ${nginx_ssl}/dhparam2048.pem 2048
  chmod 0600 ${nginx_ssl}/dhparam2048.pem
fi


### mapproxy
cd /opt/mp

cp -R mapproxy /

groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

wget -O /world_map.mbtiles --progress=dot:giga https://boundless-exchange-test.s3.amazonaws.com/world_map.mbtiles
chmod 0644 /world_map.mbtiles


### runtime
cd /opt/mp
cp entrypoint.sh /
chmod 0755 /entrypoint.sh
