# quay.io/boundlessgeo/bex-nodejs-bower-grunt
# docker build -t bex-nodejs-bower-grunt .
FROM node:10-slim
LABEL maintainer="Daniel Berry <dberry@boundlessgeo.com>"

RUN npm install -g bower grunt-cli karma && \
  apt-get update && \
  apt-get install -y python bzip2 git

CMD ["/bin/bash"]
