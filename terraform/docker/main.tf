provider "docker" {}

resource "docker_image" "dadbot-actions" {
  name         = "dadbot-actions:1.0"
  keep_locally = true
}

resource "docker_image" "dadbot-api" {
  name         = "dadbot-api:1.0"
  keep_locally = true
}

resource "docker_image" "dadbot-web" {
  name         = "dadbot-web:1.0"
  keep_locally = true
}

resource "docker_network" "backend-net" {
  name = "backend-net"
  internal = true
  driver = "macvlan"
}

resource "docker_network" "frontend-net" {
  name = "frontend-net"
  internal = false
  driver = "bridge"
}

#resource "docker_volume" "nvidia-models" {
#  name = "nvidia_models"
#}
#resource "docker_volume" "rasa-models" {
#  name = "rasa_models"
#}

resource "docker_container" "dadbot-actions" {
  image = docker_image.dadbot-actions.name
  name  = "dadbot-actions"
  hostname  = "dadbot-actions"
  ports {
    internal = 5055
  }

  networks_advanced {
    name = "backend-net"
  }
  networks_advanced {
    name = "frontend-net"
  }

  working_dir = "/app"
  user = 1000

  depends_on = [docker_network.backend-net, docker_network.frontend-net]
}

resource "docker_container" "dadbot-trainer" {
  image = docker_image.dadbot-api.name
  name  = "dadbot-trainer"
  hostname  = "dadbot-trainer"
  env = ["CUDA_AVAILABLE_DEVICES=0", "CUDA_HOME=/usr/local/cuda"]

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
    host_path = "/home/debian/workspace/models"
    container_path = "/home/debian/workspace/models"
    volume_name = "nvidia-models"
  }
  #mounts {
  #  source = "/home/debian/workspace/models"
  #  target = "/home/debian/workspace/models"
  #  type = "bind"
  #}
  volumes {
    host_path = "/home/debian/workspace/Dadbot/models"
    container_path = "/app/models"
    volume_name = "rasa-models"
  }
  #mounts {
  #  source = "/home/debian/workspace/Dadbot/models"
  #  target = "/app/models"
  #  type = "bind"
  #}

  #devices {
  #  host_path = "/dev/nvidia0"
  #  container_path = "/dev/nvidia0"
  #}
  #devices {
  #  host_path = "/dev/nvidiactl"
  #  container_path = "/dev/nvidiactl"
  #}

  working_dir = "/app"
  user = 1000
  command = ["python3", "-m", "rasa", "train", "--debug"]
}

resource "docker_container" "dadbot-connector" {
  image = docker_image.dadbot-api.name
  name  = "dadbot-connector"
  hostname  = "dadbot-connector"
  env = ["CUDA_AVAILABLE_DEVICES=0", "CUDA_HOME=/usr/local/cuda", "RASA_TELEMETRY_ENABLED=false"]

  ports {
    internal = 5005
    external = 5005
  }

  #volumes {
  #  host_path = "/home/debian/workspace/models"
  #  container_path = "/home/debian/workspace/models"
  #  volume_name = "nvidia-models"
  #}
  mounts {
    source = "/home/debian/workspace/models"
    target = "/home/debian/workspace/models"
    type = "bind"
  }
  #volumes {
  #  host_path = "/home/debian/workspace/Dadbot/models"
  #  container_path = "/app/models"
  #  volume_name = "rasa-models"
  #}
  mounts {
    source = "/home/debian/workspace/Dadbot/models"
    target = "/app/models"
    type = "bind"
  }

  networks_advanced {
    name = "frontend-net"
  }
  networks_advanced {
    name = "backend-net"
  }

  #devices {
  #  host_path = "/dev/nvidia0"
  #  container_path = "/dev/nvidia0"
  #}
  #devices {
  #  host_path = "/dev/nvidiactl"
  #  container_path = "/dev/nvidiactl"
  #}

  working_dir = "/app"
  user = 1000
  command = ["python3", "-m", "rasa", "run", "--enable-api", "--cors", "'https://dadbot-web.ddns.net:8000'", "--connector", "voice_connector.ChatInput", "--ssl-certificate=dadbot.crt", "--ssl-keyfile=dadbot.key", "--debug"]

  depends_on = [docker_network.backend-net]
}

resource "docker_container" "dadbot-web" {
  image = docker_image.dadbot-web.name
  name  = "dadbot-web.ddns.net"
  hostname  = "dadbot-web.ddns.net"
  ports {
    ip = "dadbot-web.ddns.net"
    internal = 8000
    external = 8000
  }

  networks_advanced {
    name = "frontend-net"
  }
  networks_advanced {
    name = "backend-net"
  }

  working_dir = "/app"
  user = 1000
  command = ["python3", "dadbot.py"]

  # In case of django web server
  #command = ["python3", "manage.py", "runserver"]

  depends_on = [docker_network.frontend-net, docker_network.backend-net]
}
