
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Jidnya\\AppData\\Local\\Programs\\Python\\Python310\\python.exe'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
                bat 'git --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"%PYTHON%" -m pytest -v'
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
