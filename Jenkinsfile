pipeline {
    agent any

    environment {
    PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Check Environment') {
            steps {
                sh '''
                    echo "Checking Docker..."
                    docker --version
                    docker compose version
                    docker info >/dev/null
                '''
            }
        }

        stage('Checkout') {
            steps {
                script {
                    def checkoutInfo = checkout scm
                    env.CHECKED_OUT_BRANCH = checkoutInfo.GIT_BRANCH ?: env.BRANCH_NAME ?: ''
                    env.CHECKED_OUT_COMMIT = checkoutInfo.GIT_COMMIT ?: sh(
                        returnStdout: true,
                        script: 'git rev-parse HEAD'
                    ).trim()
                }
            }
        }

        // stage('Code Quality') {
        //     steps {
        //         sh '''
        //             docker compose -p something-ci -f docker-compose.ci.yml build app
        //             docker compose -p something-ci -f docker-compose.ci.yml run --rm app \
        //                 sh -c 'ruff check . && bandit -r . -x ./tests'
        //         '''
        //     }
        // }

        stage('Django Validation') {
            steps {
                sh '''
                    docker compose -p something-ci -f docker-compose.ci.yml up -d --wait db
                    docker compose -p something-ci -f docker-compose.ci.yml run --rm app \
                        sh -c 'python manage.py check && python manage.py makemigrations --check --dry-run'
                '''
            }
        }

        stage('Database Tests') {
            steps {
                sh '''
                    docker compose -p something-ci -f docker-compose.ci.yml run --rm app \
                        sh -c 'python manage.py migrate --noinput && python manage.py migrate --check && python manage.py test --verbosity=2'
                '''
            }
        }

        stage('Build Image') {
            steps {
                script {
                    env.APP_IMAGE = "something:${env.CHECKED_OUT_COMMIT.take(12)}"
                }

                sh '''
                    docker build --tag "$APP_IMAGE" .
                    docker images "$APP_IMAGE"
                '''
            }
        }

        stage('Deploy Main') {
            when {
                expression {
                    env.BRANCH_NAME == 'main' ||
                    env.CHECKED_OUT_BRANCH == 'main' ||
                    env.CHECKED_OUT_BRANCH == 'origin/main'
                }
            }
            steps {
                withCredentials([file(credentialsId: 'django-production-env', variable: 'DEPLOY_ENV_FILE')]) {
                    sh 'docker compose --env-file "$DEPLOY_ENV_FILE" -f dockercompose.yaml up -d --no-build --force-recreate --remove-orphans'
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker compose -p something-ci \
                -f docker-compose.ci.yml down \
                --volumes --remove-orphans || true
            '''
        }

        success {
            echo 'CI pipeline and Docker image build completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Please check the console output.'
        }
    }
}
