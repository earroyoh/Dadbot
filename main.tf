provider "docker" {}

resource "docker_image" "dadbot" {
  name         = "dadbot:1.0"
  keep_locally = true
}

resource "docker_container" "dadbot" {
  image = docker_image.dadbot.name
  name  = "dadbot"
  hostname  = "dadbot"
  ports {
    internal = 5000
  }
  ports {
    internal = 5002
  }
  ports {
    internal = 5005
  }
  ports {
    internal = 5055
    external = 5055
  }
  ports {
    internal = 8000
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
}
