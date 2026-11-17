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

    stages {

        stage('Check Environment') {
            steps {
                sh '''
                    echo "Checking Python..."
                    python3.11 --version

                    echo "Checking Docker..."
                    docker --version
                    docker info
                '''
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    /opt/homebrew/bin/python3.11 -m venv .venv

                    .venv/bin/python -m pip install --upgrade pip

                    .venv/bin/python -m pip install -r requirements.txt ruff bandit

                    .venv/bin/ruff check .

                    .venv/bin/bandit -r . -x ./.venv,./tests
                '''
            }
        }

        stage('Django Validation') {
            steps {
                sh '''
                    export DJANGO_SECRET_KEY=ci-only-secret
                    export DB_NAME=test_db
                    export DB_USER=test_user
                    export DB_PASSWORD=test_password
                    export DB_HOST=127.0.0.1
                    export DB_PORT=5433
                    export DJANGO_SETTINGS_MODULE=something.settings.development

                    .venv/bin/python manage.py check

                    .venv/bin/python manage.py makemigrations --check --dry-run
                '''
            }
        }

        stage('Database Tests') {
            steps {
                sh '''
                    docker compose -p something-ci \
                    -f docker-compose.ci.yml up -d --wait db

                    export DJANGO_SECRET_KEY=ci-only-secret
                    export DB_NAME=test_db
                    export DB_USER=test_user
                    export DB_PASSWORD=test_password
                    export DB_HOST=127.0.0.1
                    export DB_PORT=5433
                    export DJANGO_SETTINGS_MODULE=something.settings.development

                    .venv/bin/python manage.py migrate --noinput

                    .venv/bin/python manage.py migrate --check

                    .venv/bin/python manage.py test --verbosity=2
                '''
            }
        }

        stage('Build Image') {
            steps {
                script {
                    env.APP_IMAGE = "something:${env.GIT_COMMIT.take(12)}"
                }

                sh '''
                    docker build --tag "$APP_IMAGE" .
                    docker images "$APP_IMAGE"
                '''
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
