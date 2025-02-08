variable "dadbot-web-url" {
  type    = string
  default = "dadbot-web.ddns.net"
}

variable "OPENAI_API_KEY" {
  type    = string
  default = ""
}

variable "workspace-dir" {
  type    = string
  default = "~/workspace/Dadbot"
}

variable "registry" {
  type    = string
  default = ""
}

variable "model" {
  type    = string
  default = "gpt-4-turbo-preview"
}
