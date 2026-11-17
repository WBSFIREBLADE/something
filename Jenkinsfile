pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    // Requires the GitHub plugin and a webhook configured to notify Jenkins.
    triggers {
        githubPush()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt ruff bandit
                    .venv/bin/ruff check .
                    .venv/bin/bandit -r . -x ./.venv,./tests
                '''
            }
        }

        stage('Django Validation') {
            steps {
                sh '''
                    export SECRET_KEY=ci-only-secret
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
                    docker compose -p something-ci -f docker-compose.ci.yml up -d --wait db
                    export SECRET_KEY=ci-only-secret
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
                sh 'docker build --tag "$APP_IMAGE" .'
            }
        }

        stage('Deploy Main') {
            when {
                branch 'main'
            }
            steps {
                sh 'docker compose -f dockercompose.yaml up -d --no-build --remove-orphans'
            }
        }
    }

    post {
        always {
            sh 'docker compose -p something-ci -f docker-compose.ci.yml down --volumes --remove-orphans || true'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs for details.'
        }
    }
}
