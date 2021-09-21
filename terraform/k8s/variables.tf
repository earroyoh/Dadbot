variable "dadbot-namespace" {
  type    = string
  default = "rasa"
}

variable "dadbot-web-url" {
  type    = string
  default = "dadbot-web.ddns.net"
}

variable "OPENAI_API_KEY" {
  type    = string
}

variable "workspace-dir" {
  type    = string
  default = "~/workspace/Dadbot"
}

variable "external-ip" {
  type    = string
}

variable "registry" {
  type    = string
  default = ""
}
