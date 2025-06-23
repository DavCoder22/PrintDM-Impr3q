variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "postgres_user" {
  description = "PostgreSQL username"
  type        = string
  default     = "postgres"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "postgres_db" {
  description = "PostgreSQL database name"
  type        = string
  default     = "printing_db"
}

variable "services" {
  description = "Configuration for each service"
  type = map(object({
    port = number
    env  = map(string)
  }))
  default = {
    printers_service = {
      port = 8000
      env  = {}
    }
    monitoring_service = {
      port = 8001
      env  = {}
    }
    calibration_service = {
      port = 8002
      env  = {}
    }
  }
}
