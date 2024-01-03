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
					def convertWindowsPathToUnixStyle(String windowsPath) {
						// Determine the OS
						// OS-specific commands
						def os = env.OS
						def isUnix = (os == null || os.contains('Windows') == false)
					
						if (isUnix){
							return windowsPath
						} else {
							// Replace backslashes with forward slashes
							def unixStylePath = windowsPath.replace('\\', '/')
						
							// Replace 'C:' with '/c'
							unixStylePath = unixStylePath.replaceFirst(/([A-Za-z]):/, '/$1')
							// Convert to lowercase drive letter (optional, based on preference/requirement)
							return unixStylePath.toLowerCase()						
						}
					}
					
					def workspacePath = convertWindowsPathToUnixStyle(env.WORKSPACE)
	
					// Log the OS and workspace path for troubleshooting
					echo "Running on ${isUnix ? 'Unix/Linux' : 'Windows'}"
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