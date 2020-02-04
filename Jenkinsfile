#!/usr/bin/env groovy

pipeline {
    agent any
    options {
        ansiColor('xterm')
    }
    stages {
        stage('Cleanup') {
            steps {
                script {
                    sh "git clean -dfx"
                }
            }
        }
        stage('Run Tests') {
            steps {
                script {
                    def envs = sh(
                        script: "tox -l",
                        returnStdout: true
                    ).trim().split('\n')

                    def cmds = envs.collectEntries({
                        tox_env -> [
                            tox_env,
                            {
                                stage("Tox env ${tox_env}") {
                                    sh "tox -vve $tox_env"
                                }
                            }
                        ]
                    })

                    parallel(cmds)
                }
            }
        }
    }
}
