pipeline {
    agent any

    environment {
        SCRIPT_PATH = 'src/dremio_cloner.py' // Path to your Python script in the Git repository
		PROJECT_NAME = 'demo_project_01'
		DOCKER_IMAGE = 'python-golden'
		DOCKER_TAG = '31'
    }

    stages {
        stage('Run Dremio cloner') {
            steps {
                script {
					// Determine the OS
					def osName = System.properties['os.name'].toLowerCase()
					
					// Set the workspace path based on the OS	
					def workspacePath = osName.contains('windows') ? env.WORKSPACE : env.WORKSPACE.replace("\\", "/")
	
					// Log the OS and workspace path for troubleshooting
					echo "Running on ${osName.contains('windows') ? 'Unix/Linux' : 'Windows'}"
					echo "Workspace path: ${workspacePath}"
					
                    // Run the Python script within the Docker container
                    docker.withRegistry("https://${env.DOCKER_REGISTRY}", env.DOCKER_REGISTRY_CREDENTIALS_ID) {
                        // Create a Docker image object
                        def pythonImage = docker.image("${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}/${env.DOCKER_IMAGE}:${env.DOCKER_TAG}")
                        // Run the container with the script mounted and execute the Python script
                        pythonImage.inside("-v ${workspacePath}:/app/workspace") {
                            sh """
								python /app/workspace/src/dremio_cloner.py /app/workspace/config/config_read_dremio_cloud.json
								python /app/workspace/src/dremio_cloner.py /app/workspace/config/config_write_dremio_cloud.json
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