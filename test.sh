#! /bin/bash

mv exchange/core/fixtures/initial_data.json exchange/core/fixtures/initial_data_tmp.json
mv exchange/core/fixtures/boundless.json exchange/core/fixtures/initial_data.json
python manage.py test
mv exchange/core/fixtures/initial_data.json exchange/core/fixtures/boundless.json
mv exchange/core/fixtures/initial_data_tmp.json exchange/core/fixtures/initial_data.json
