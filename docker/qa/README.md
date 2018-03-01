### Regression Tests for Boundless Exchange

**Note:** Run the following command in this `qa` directory.

```bash
docker run --rm -v $PWD:/katalon/katalon/source:ro \
                -e BROWSER_TYPE="Chrome" \
                -e TEST_SUITE_PATH="Test Suites/regression" \
                -e DOCKER_PROXY_ALIAS="nginx" \
                quay.io/boundlessgeo/b7s-katalon:federal
```

Environment Variables:
+ BROWSER_TYPE - Options: Firefox, Chrome
+ TEST_SUITE_PATH - Specify the test suite file (without extension .ts)
+ DOCKER_PROXY_ALIAS - Proxy alias to add to hosts file associated with docker host entry

### Steps to use in Non Docker Katalon Studio

1. Download Katalon Studio [here](https://www.katalon.com/)
2. Import the qa project e.g. the directory that this README resides.
