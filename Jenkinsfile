
pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat 'python --version'
                bat 'git --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'python -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Digital Notice Board build passed!'
        }
        failure {
            echo 'FAILED: Check Console Output for details.'
        }
    }
}
