node {
  withCredentials(
    [string(credentialsId: 'boundlessgeoadmin-token', variable: 'GITHUB_TOKEN'),
     string(credentialsId: 'connect-ftp-combo', variable: 'CONNECT_FTP'),
     string(credentialsId: 'sonar-jenkins-pipeline-token', variable: 'SONAR_TOKEN')]) {


    try {
      stage('Checkout'){
        setEnvs()

        checkout scm
        sh """
          git submodule update --init
          echo "Running ${env.BUILD_ID} on ${env.JENKINS_URL}"
        """
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

      // TODO: Move changes to core config
      stage('M-BEx Edits'){
        sh """
          cat managed-services/exchange-entrypoint.sh > docker/exchange/entrypoint.sh
        """
      }

      stage('Setup'){
        sh """
          docker pull 'quay.io/boundlessgeo/sonar-maven-py3-alpine'
          docker pull 'quay.io/boundlessgeo/bex-nodejs-bower-grunt:v0.10.x'
          docker-compose down
          docker system prune -f
        """
      }

      stage('Style Checks'){
        parallel (
            "pycodestyle" : {
              bashDocker(
                'quay.io/boundlessgeo/sonar-maven-py3-alpine',
                'pycodestyle exchange --ignore=E722,E731'
              )
            },
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

      stage('Build Maploom'){
        bashDocker(
          'quay.io/boundlessgeo/bex-nodejs-bower-grunt:v0.10.x',
          'rm -fr vendor/maploom/node_modules vendor/maploom/package-lock.json && . docker/devops/helper.sh && build-maploom'
        )
      }

      stage('Build Images'){
        sh """
          docker rm -f \$(docker ps -aq) || echo "no containers to remove"
          docker-compose up --build --force-recreate -d
        """
      }

      stage('Start Containers'){
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
      // Chopped for Managed Services to avoid test duplication
      stage('py.test'){
        sh """
          docker-compose exec -T exchange /bin/bash -c '/code/docker/exchange/run_tests.sh'
        """
      }

      if (env.BRANCH_NAME == 'master') {
        stage('SonarQube Analysis') {
          sh """
            docker run -e SONAR_HOST_URL='https://sonar-ciapi.boundlessgeo.io' \
                       -e SONAR_TOKEN=$SONAR_TOKEN \
                       -v \$(pwd -P):/code \
                       -w /code quay.io/boundlessgeo/sonar-maven-py3-alpine bash \
                       -c '. docker/devops/helper.sh && sonar-scan'
            """
        }
      }

      if (gitTagCheck()) {
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
      } */

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
