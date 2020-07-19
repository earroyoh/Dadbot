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
    external = 5000
  }
  volumes {
    host_path = "/home/debian/workspace/Dadbot/models"
    container_path = "/app/Dadbot/models"
    volume_name = "models"
  }
  working_dir = "/app/Dadbot"
  user = 1001
  command = ["python3", "-m", "flask", "run",  "--host=0.0.0.0"]
}
