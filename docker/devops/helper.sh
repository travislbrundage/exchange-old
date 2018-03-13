#!/bin/bash

# Code style checks
function lint {
    echo "-------> exchange flake8"
    flake8 --ignore=F405,E722,E731 exchange
    echo "-------> exchange yamllint"
    yamllint -d "{extends: relaxed, rules: {line-length: {max: 120}}}" $(find . -name "*.yml" -not -path "./vendor/*")
}

function makemigrations-check {
    if [[ ! $(python manage.py makemigrations --dry-run) == "No changes detected" ]]; then
      python manage.py makemigrations --dry-run --verbosity 3
      echo "Please commit your migrations"
      exit 1
    else
      echo "No migrations detected"
    fi
}

# Jenkins function for exchange healthcheck
function exchange-healthcheck {
    for i in $(seq 1 20);
        do echo $(docker inspect --format '{{ .State.Health.Status }}' exchange) | grep -w healthy && s=0 && break || \
           s=$? && echo "exchange is not ready, trying again in 30 seconds" && sleep 30;
    done; docker-compose logs && (exit $s)
}

# Jenkins function to get exchange version via python3
function py3-bex-version {
    python3 -c "print(__import__('exchange').semantic_version())"
}

# function to build maploom from src
function build-maploom {
    pushd vendor/maploom
    npm install
    bower install --allow-root
    grunt
    PACKAGE_VERSION=$(cat package.json \
    | grep version \
    | head -1 \
    | awk -F: '{ print $2 }' \
    | sed 's/[",]//g')
    VERSION=${PACKAGE_VERSION// /}
    echo "{% load i18n static %}
    <link rel=\"stylesheet\" type=\"text/css\" href=\"{% static 'maploom/assets/MapLoom-$VERSION.css' %}\"/>
    <script type=\"text/javascript\" src=\"{% static 'maploom/assets/MapLoom-$VERSION.js' %}\"/>" > bin/_maploom_js.html
    sed -n '/body class="maploom-body">/,/body>/p' bin/index.html > bin/index_body.html
    sed '/body>/d' bin/index_body.html > bin/index_body_no_tag.html
    echo '{% load staticfiles i18n %}{% verbatim %}' > bin/_maploom_map.html
    cat bin/index_body_no_tag.html >> bin/_maploom_map.html
    echo '{% endverbatim %}' >> bin/_maploom_map.html
    if [[ -f /code/exchange/maploom/templates/maploom/_maploom_js.html ]]; then
      rm /code/exchange/maploom/templates/maploom/_maploom_js.html
    fi
    cp bin/_maploom_js.html /code/exchange/maploom/templates/maploom/_maploom_js.html
    if [[ -f /code/exchange/maploom/templates/maploom/_maploom_map.html ]]; then
      rm /code/exchange/maploom/templates/maploom/_maploom_map.html
    fi
    cp bin/_maploom_map.html /code/exchange/maploom/templates/maploom/_maploom_map.html
    if [[ -f /code/exchange/maploom/templates/maps/maploom.html ]]; then
      rm /code/exchange/maploom/templates/maps/maploom.html
    fi
    cp bin/maploom.html /code/exchange/maploom/templates/maps/maploom.html
    if [[ -d /code/exchange/maploom/static/maploom ]]; then
      rm -r /code/exchange/maploom/static/maploom
    fi
    mkdir /code/exchange/maploom/static/maploom
    cp -r bin/assets /code/exchange/maploom/static/maploom/assets
    cp -r bin/fonts /code/exchange/maploom/static/maploom/fonts
    rm -f package-lock.json
    popd
}
