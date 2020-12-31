provider "docker" {}

resource "docker_image" "dadbot" {
  name         = "dadbot:1.0"
  keep_locally = true
}

resource "docker_image" "dadbot-api" {
  name         = "dadbot-api:1.0"
  keep_locally = true
}

resource "docker_network" "backend-net" {
  name = "backend-net"
  internal = true
}

resource "docker_network" "frontend-net" {
  name = "frontend-net"
}

#resource "docker_volume" "nvidia_models" {
#  name = "nvidia_models"
#}

resource "docker_container" "dadbot-actions" {
  image = docker_image.dadbot.name
  name  = "dadbot-actions"
  hostname  = "dadbot-actions"
  ports {
    internal = 5055
    external = 5055
  }
  networks_advanced {
    name = "backend-net"
    aliases = ["private"]
  }

  working_dir = "/app"
  user = 1000
}

resource "docker_container" "dadbot-trainer" {
  image = docker_image.dadbot-api.name
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
    host_path = "/home/debian/workspace/Dadbot"
    container_path = "/app/Dadbot"
    volume_name = "models"
  }
  networks_advanced {
    name = "backend-net"
    aliases = ["private"]
  }
  working_dir = "/app/Dadbot"
  user = 1000
  command = ["python3", "-m", "rasa", "train", "--debug"]
}

resource "docker_container" "dadbot-connector" {
  image = docker_image.dadbot-api.name
  name  = "dadbot-connector"
  hostname  = "dadbot-connector"
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
    host_path = "/home/debian/workspace/Dadbot"
    container_path = "/app/Dadbot"
    volume_name = "rasa-app"
  }
  networks_advanced {
    name = "backend-net"
    aliases = ["private"]
  }

  working_dir = "/app/Dadbot"
  user = 1000
  command = ["python3", "-m", "rasa", "run", "--enable-api", "--cors", "'*'", "--connector", "voice_connector.ChatInput", "--debug"]

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
  networks_advanced {
    name = "frontend-net"
    aliases = ["public"]
  }
  networks_advanced {
    name = "backend-net"
    aliases = ["private"]
  }

  working_dir = "/app"
  user = 1001
  command = ["run", "python3", "dadbot.py"]

  depends_on = [docker_container.dadbot-trainer]
}
