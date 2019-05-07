pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                echo 'Testing..'
                sh "source init.sh && python heppy/test/suite.py"
            }
        }
    }
}
