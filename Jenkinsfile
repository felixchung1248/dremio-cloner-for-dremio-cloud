pipeline {
    agent any

    parameters {
        string(name: 'FOLDER_PATH', description: 'Folder path of the dataset')
        string(name: 'DATASET_NAME', description: 'Dataset name')
    }

    environment {
        SCRIPT_PATH = 'src/dremio_cloner.py' // Path to your Python script in the Git repository
		PROJECT_NAME = 'demo_project_01'
		DOCKER_IMAGE = 'python-golden'
		DOCKER_TAG = '11'
        DREMIO_USR_SANDBOX = credentials('dremio-usr-sandbox')
        DREMIO_PW_SANDBOX = credentials('dremio-pw-sandbox')
    }

    stages {
        stage('Pre-flight Check') {
            steps {
                script {
                    if (!params.FOLDER_PATH) {
                        error "The FOLDER_PATH parameter is missing. Please provide folder path for the dataset."
                    }
                    if (!params.DATASET_NAME) {
                        error "The DATASET_NAME parameter is missing. Please provide the dataset name."
                    }
                }
            }
        }

        stage('Run Dremio cloner') {
            steps {
                script {					
					
                    // Run the Python script within the Docker container
                    docker.withRegistry("https://${env.DOCKER_REGISTRY}", env.DOCKER_REGISTRY_CREDENTIALS_ID) {
                        // Create a Docker image object
                        def pythonImage = docker.image("${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}/${env.DOCKER_IMAGE}:${env.DOCKER_TAG}")
                        // Run the container with the script mounted and execute the Python script
                        pythonImage.inside("-v ${env.WORKSPACE}:/app/workspace") {
                            sh """
                                python3 /app/workspace/replace_param.py json_file_path=config/config_read_dremio_cloud.json endpoint=${env.DREMIO_URL_SANDBOX} username=${env.DREMIO_USR_SANDBOX} password=${env.DREMIO_PW_SANDBOX} dremio_cloud_org_id=${env.DREMIO_CLOUD_ORG_ID_SANDBOX} dremio_cloud_project_id=${env.DREMIO_CLOUD_PROJECT_ID_SANDBOX} space.folder.filter='${env.FOLDER_PATH}' vds.filter.names='${env.DATASET_NAME}'
								python3 /app/workspace/src/dremio_cloner.py /app/workspace/config/config_read_dremio_cloud.json_filled
								python3 /app/workspace/src/dremio_cloner.py /app/workspace/config/config_write_dremio_cloud.json
							   """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // Optional: clean up
            cleanWs()
        }
    }
}