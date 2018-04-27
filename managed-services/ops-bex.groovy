/*
About
-----
Boundless Exchange uses the Jenkins Multibranch Pipeline, which creates a set of Pipeline projects according to
detected branches in one SCM repository. The Jenkins master instance does not run any jobs, instead, it spins up
temporary instances based on an Amazon Machine Image (AMI). The AMI includes docker, docker-compose and git cli
(with ssh credentials). This method was used to save money and also to allow for all stages to easily be run on a
new Jenkins server.

Shared Libraries Required
-------------------------
https://github.com/boundlessgeo/bex-pipelib
*/

node {
  withCredentials([
    string(credentialsId: 'boundlessgeoadmin-token', variable: 'GITHUB_TOKEN'),
    string(credentialsId: 'connect-ftp-combo', variable: 'CONNECT_FTP'),
    string(credentialsId: 'sq-boundlessgeo-token', variable: 'SONAR_TOKEN'),
    string(credentialsId: 'sonarqube-github-token', variable: 'SONAR_GITHUB_TOKEN'),
  ]) {

    try {
      /*
      This stage consists of git checkout of the exchange repository (private),
      https://github.com/boundlessgeo/exchange/blob/master/.gitmodules and
      https://github.com/boundlessgeo/exchange-mobile-extension.
      */
      stage('Checkout'){
        setEnvs()

        checkout scm
        echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
        checkout([$class: 'GitSCM',
                  branches: [[name: '*/master']],
                  doGenerateSubmoduleConfigurations: false,
                  extensions: [[$class: 'RelativeTargetDirectory',
                                relativeTargetDir: './vendor/exchange-mobile-extension']],
                  submoduleCfg: [],
                  userRemoteConfigs: [[credentialsId: 'BoundlessAdminGitHub',
                                       url: 'https://github.com/boundlessgeo/exchange-mobile-extension.git']]])
        sh """
          # https://issues.jenkins-ci.org/browse/JENKINS-44909
          rm -r vendor/exchange-mobile-extension@tmp
        """
      }

      /*
      This stage sets up the temporary host by pulling a key image, ensuring docker-compose environment
      is cleaned up by shutting down any existing networks, clearing images and volumes.
      */
      stage('Setup'){
        sh """
          docker pull 'quay.io/boundlessgeo/sonar-maven-py3-alpine'
          docker-compose down
          docker system prune -f
        """
      }

      /*
      This stage runs parallel jobs for various style checks.
      */
      stage('Style Checks'){
        parallel (
            "yamllint" : {
              bashDocker(
                'quay.io/boundlessgeo/sonar-maven-py3-alpine',
                'yamllint -d "{extends: relaxed, rules: {line-length: {max: 120}}}" $(find . -name "*.yml" -not -path "./vendor/*")'
              )
            },
            "flake8" : {
              bashDocker(
                'quay.io/boundlessgeo/sonar-maven-py3-alpine',
                'flake8 --ignore=F405,E722,E731 exchange'
              )
            }
        )
      }

      /*
      This stage builds maploom form the source submodule and adds key files to exchange static.
      */
      stage('Build Maploom'){
        bashDocker(
          'quay.io/boundlessgeo/bex-nodejs-bower-grunt',
          '. docker/devops/helper.sh && build-maploom && rm -fr vendor/maploom/node_modules'
        )
      }

      /*
      This stage builds the required docker images.
      */
      stage('Build Images'){
        sh """
          docker rm -f \$(docker ps -aq) || echo "no containers to remove"
          docker-compose build --force-rm --no-cache --pull
        """
      }

      /*
      This stage starts the containers and verifies exchange container is healthy.
      */
      stage('Start Containers'){
        sh """
          docker-compose up -d
        """
        timeout(time: 10, unit: 'MINUTES')  {
          waitUntil {
            script {
              def r = sh script: 'wget -q http://localhost -O /dev/null', returnStatus: true
              return (r == 0);
            }
          }
        }
        sh """
          docker-compose logs
        """
      }

      /*
      This stage runs safety and OWASP dependency check on source.
      */
      stage('Dependency Checks'){
        parallel (
          // "Migration Check" : {
          //  sh """
          //    docker-compose exec -T exchange /bin/bash -c '. docker/devops/helper.sh && makemigrations-check'
          //  """
          // },
          "Safety Check" : {
            sh """
              docker-compose exec -T exchange /bin/bash -c 'pip install safety && pip freeze | safety check --stdin --full-report'
            """
          },
          "Dependency Check" : {
            bashDocker(
              'quay.io/boundlessgeo/b7s-sonarqube-scanner',
              'dependency-check --project exchange \
                                --disableBundleAudit \
                                --disableAssembly \
                                --out . \
                                --scan . \
                                -f ALL \
                                --cveUrl12Base "https://nvd.nist.gov/feeds/xml/cve/1.2/nvdcve-%d.xml.gz" \
                                --cveUrl20Base "https://nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-%d.xml.gz" \
                                --cveUrl12Modified "https://nvd.nist.gov/feeds/xml/cve/1.2/nvdcve-modified.xml.gz" \
                                --cveUrl20Modified "https://nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-modified.xml.gz" \
               && cat dependency-check-report.json'
            )
          }
        )
      }

      /*
      This stage runs py.test against all tests in exchange, coverage is also provided during this step.
      */
      stage('Functional Tests'){
        sh """
          docker-compose exec -T exchange /bin/bash \
                              -c 'pip install pytest-cov \
                                  && export DJANGO_SETTINGS_MODULE="exchange.settings" \
                                  && export PYTEST=1 \
                                  && py.test --cov-report term \
                                             --cov-report xml \
                                             --cov=exchange exchange/tests/ \
                                             --disable-pytest-warnings'
        """
      }

      /*
      This stage runs regression tests for Mozilla Firefox using katalon.
      */
      /*
      // Chopped for Managed Services to avoid test duplication
      stage('Firefox Tests'){
        katalonDocker([browser: 'Firefox', rpath: 'docker/qa'], 'Test Suites/regression')
      }
      */

      /*
      This stage runs regression tests for Google Chrome using katalon.
      */
      /*
      // Chopped for Managed Services to avoid test duplication
      stage('Chrome Tests'){
        katalonDocker([browser: 'Chrome', rpath: 'docker/qa'], 'Test Suites/regression')
      }
      */

      /*
      This stage runs runs static code analysis using SonarQube.
      */
      /*
      // Chopped for Managed Services to avoid test duplication
      stage('SonarQube Analysis') {
        // Format: Jenkins Build Number.Github PR number if PR
        def projectVersion = (env.CHANGE_ID != null) ? "${env.BUILD_NUMBER}.${env.CHANGE_ID}" : "${env.BUILD_NUMBER}"

        if (env.BRANCH_NAME == 'master') {
          // Publish to SonarQube
          sh """
            docker run -v \$(pwd -P):/code \
                       -w /code quay.io/boundlessgeo/b7s-sonarqube-scanner bash \
                       -c 'sonar-scanner -Dsonar.host.url=https://sq.boundlessgeo.io \
                                         -Dsonar.login=$SONAR_TOKEN \
                                         -Dsonar.projectKey=exchange \
                                         -Dsonar.projectVersion=${projectVersion} \
                                         -Dsonar.projectName=exchange \
                                         -Dsonar.dependencyCheck.reportPath=dependency-check-report.xml \
                                         -Dsonar.dependencyCheck.htmlReportPath=dependency-check-report.html \
                                         -Dsonar.sources=exchange \
                                         -Dsonar.language=py \
                                         -Dsonar.python.pylint=/usr/bin/pylint \
                                         -Dsonar.python.coverage.reportPath=coverage.xml'
          """
        } else if (env.CHANGE_ID != null) {
          // Preview and publish to GitHub
          sh """
            docker run -v \$(pwd -P):/code \
                       -w /code quay.io/boundlessgeo/b7s-sonarqube-scanner bash \
                       -c 'sonar-scanner -Dsonar.analysis.mode=preview \
                                         -Dsonar.host.url=https://sq.boundlessgeo.io \
                                         -Dsonar.login=$SONAR_TOKEN \
                                         -Dsonar.github.oauth=${SONAR_GITHUB_TOKEN} \
                                         -Dsonar.projectKey=exchange \
                                         -Dsonar.projectVersion=${projectVersion} \
                                         -Dsonar.projectName=exchange \
                                         -Dsonar.dependencyCheck.reportPath=dependency-check-report.xml \
                                         -Dsonar.dependencyCheck.htmlReportPath=dependency-check-report.html \
                                         -Dsonar.sources=exchange \
                                         -Dsonar.language=py \
                                         -Dsonar.python.pylint=/usr/bin/pylint \
                                         -Dsonar.python.coverage.reportPath=coverage.xml'
          """
        } else {
          // No reporting if not master or a PR
          echo "SonarQube Analysis was not performed, please submit a PR for analysis"
        }
      }
      */

      /*
      This stage uploads the documentation to Boundless Connect if the commit was tagged.
      */
      /*
      // Chopped for Managed Services to avoid test duplication
      if (env.BRANCH_NAME == 'master' && gitTagCheck()) {
        stage('Update Connect Docs') {
          sh """
            docker run --rm -e CONNECT_FTP=$CONNECT_FTP \
                       -v \$(pwd -P):/code \
                       -w /code quay.io/boundlessgeo/sonar-maven-py3-alpine bash \
                       -c '. docker/devops/helper.sh && \
                           lftp -e "set ftp:ssl-allow no; \
                                    mkdir /site/wwwroot/docs/exchange/`py3-bex-version`; \
                                    mirror -R -e exchange/static/docs/html /site/wwwroot/docs/exchange/`py3-bex-version`; \
                                    mirror -R -e exchange/static/docs/html /site/wwwroot/docs/exchange/latest; \
                                    quit" \
                                -u $CONNECT_FTP \
                                waws-prod-ch1-017.ftp.azurewebsites.windows.net'
            """
        }
      }
      */

      currentBuild.result = "SUCCESS"
    }
    catch (err) {

      currentBuild.result = "FAILURE"
        throw err
    }

    stage('Publish') {
      quayLogin()

      // Tag images appropriately
      sh """
        docker tag bex/exchange:latest quay.io/boundlessgeo/ops-bex-exchange:${BEX_VERSION}
        docker tag bex/geoserver:latest quay.io/boundlessgeo/ops-bex-geoserver:${BEX_VERSION}
        docker tag rabbitmq:3.6-management-alpine quay.io/boundlessgeo/ops-bex-taskqueue:${BEX_VERSION}
      """

      // Push images to Quay
      sh """
        docker push quay.io/boundlessgeo/ops-bex-exchange:${BEX_VERSION}
        docker push quay.io/boundlessgeo/ops-bex-geoserver:${BEX_VERSION}
        docker push quay.io/boundlessgeo/ops-bex-taskqueue:${BEX_VERSION}
      """
    }

    stage('Post') {
      // Success or failure, always send notifications
      echo currentBuild.result
      sh """
        docker-compose logs
        docker-compose down
        docker system prune -f
        """
      notifyBuild(currentBuild.result)
    }
  }
}

def setEnvs() {
  if ( BRANCH_NAME == 'master') {
    env.BEX_VERSION = 'latest'
  } else
    env.BEX_VERSION = '$BRANCH_NAME'
}

// Slack Integration
def notifyBuild(String buildStatus = currentBuild.result) {

  // generate a custom url to use the blue ocean endpoint
  def jobName =  "${env.JOB_NAME}".split('/')
  def repo = jobName[0]
  def pipelineUrl = "${env.JENKINS_URL}blue/organizations/jenkins/${repo}/detail/${env.BRANCH_NAME}/${env.BUILD_NUMBER}/pipeline"
  // Default values
  def colorName = 'RED'
  def colorCode = '#FF0000'
  def subject = "${buildStatus}\nJob: ${env.JOB_NAME}\nBuild: ${env.BUILD_NUMBER}\nJenkins: ${pipelineUrl}\n"
  def summary = (env.CHANGE_ID != null) ? "${subject}\nAuthor: ${env.CHANGE_AUTHOR}\n${env.CHANGE_URL}\n" : "${subject}"

  // Override default values based on build status
  if (buildStatus == 'SUCCESS') {
    colorName = 'GREEN'
    colorCode = '#228B22'
  }

  // Send notifications
  slackSend (color: colorCode, message: summary, channel: '#exchange-bots')
}

def quayLogin() {
  withCredentials([string(credentialsId: 'quayJenkins', variable: 'QUAY_PW')]) {
    sh """
      set +x
      docker login -u="boundlessgeo+ciapi_jenkins" -p="${QUAY_PW}" quay.io
    """
  }
}
