pipeline {
  agent any

  stages {
    stage('Test') {
      steps{
        sh 'python3 -m venv venv'
        dir('backend') {
          sh '. ../venv/bin/activate && pip3 install -r requirements.txt && pylint_runner'
        }
      }
    }
  }

  post {
    always {
        cleanWs()
    }
  }
}
