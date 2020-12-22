provider "docker" {}

resource "docker_image" "dadbot" {
  name         = "dadbot:1.0"
  keep_locally = true
}

resource "docker_container" "dadbot-trainer" {
  image = docker_image.dadbot.name
  name  = "dadbot-trainer"
  hostname  = "dadbot-trainer"
  ports {
    internal = 5000
  }
  ports {
    internal = 5002
  }
  ports {
    internal = 5005
  }
  volumes {
    host_path = "/home/debian/workspace/Dadbot/models"
    container_path = "/app/models"
    volume_name = "models"
  }
  volumes {
    host_path = "/home/debian/workspace/Dadbot/data"
    container_path = "/app/data"
    volume_name = "data"
  }
  working_dir = "/app"
  user = 1000
  command = ["run", "python3", "-m", "rasa", "train", "--debug"]
}

resource "docker_container" "dadbot-actions" {
  image = docker_image.dadbot.name
  name  = "dadbot-actions"
  hostname  = "dadbot-actions"
  ports {
    internal = 5055
    external = 5055
  }
  working_dir = "/app"
  user = 1000
}

resource "docker_container" "dadbot-api" {
  image = docker_image.dadbot.name
  name  = "dadbot-api"
  hostname  = "dadbot-api"
  ports {
    internal = 5005
    external = 5005
  }
  volumes {
    host_path = "/home/debian/workspace/models"
    container_path = "/home/debian/workspace/models"
    volume_name = "nvidia_models"
  }
  volumes {
    host_path = "/home/debian/workspace/Dadbot/models"
    container_path = "/app/models"
    volume_name = "models"
  }
  volumes {
    host_path = "/home/debian/workspace/Dadbot/data"
    container_path = "/app/data"
    volume_name = "data"
  }
  working_dir = "/app"
  user = 1000
  command = ["run", "python3", "-m", "rasa", "run", "-m", "/app/models", "--enable-api", "--cors", "'*'", "--connector", "voice_connector.ChatInput", "--debug"]

  depends_on = [docker_container.dadbot-trainer]
}

resource "docker_container" "dadbot-web" {
  image = docker_image.dadbot.name
  name  = "dadbot-web"
  hostname  = "dadbot-web"
  ports {
    internal = 8000
    external = 8000
  }
  working_dir = "/app"
  user = 1001
  command = ["run", "python3", "dadbot.py"]

  depends_on = [docker_container.dadbot-trainer]
}
