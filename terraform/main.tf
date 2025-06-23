terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.19.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Network
resource "docker_network" "printing_network" {
  name = "printing_network"
}

# PostgreSQL Database
resource "docker_volume" "postgres_data" {
  name = "postgres_data"
}

resource "docker_image" "postgres" {
  name         = "postgres:13-alpine"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "postgres"
  image = docker_image.postgres.image_id
  
  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres",
    "POSTGRES_DB=printing_db"
  ]
  
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }
  
  networks_advanced {
    name = docker_network.printing_network.name
  }
  
  ports {
    internal = 5432
    external = 5432
  }
  
  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U postgres"]
    interval = "5s"
    timeout  = "5s"
    retries  = 5
  }
}

# Printers Service
resource "docker_image" "printers_service" {
  name = "printing-domain/printers-service:latest"
  build {
    context = "../services/printers-service"
  }
}

resource "docker_container" "printers_service" {
  name  = "printers-service"
  image = docker_image.printers_service.image_id
  
  env = [
    "APP_ENV=production",
    "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/printing_db",
    "LOG_LEVEL=info"
  ]
  
  networks_advanced {
    name = docker_network.printing_network.name
  }
  
  ports {
    internal = 8000
    external = 8000
  }
  
  depends_on = [docker_container.postgres]
}

# Monitoring Service
resource "docker_image" "monitoring_service" {
  name = "printing-domain/monitoring-service:latest"
  build {
    context = "../services/monitoring-service"
  }
}

resource "docker_container" "monitoring_service" {
  name  = "monitoring-service"
  image = docker_image.monitoring_service.image_id
  
  env = [
    "APP_ENV=production",
    "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/printing_db",
    "LOG_LEVEL=info"
  ]
  
  networks_advanced {
    name = docker_network.printing_network.name
  }
  
  ports {
    internal = 8001
    external = 8001
  }
  
  depends_on = [docker_container.postgres]
}

# Calibration Service
resource "docker_image" "calibration_service" {
  name = "printing-domain/calibration-service:latest"
  build {
    context = "../services/calibration-service"
  }
}

resource "docker_container" "calibration_service" {
  name  = "calibration-service"
  image = docker_image.calibration_service.image_id
  
  env = [
    "APP_ENV=production",
    "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/printing_db",
    "LOG_LEVEL=info"
  ]
  
  networks_advanced {
    name = docker_network.printing_network.name
  }
  
  ports {
    internal = 8002
    external = 8002
  }
  
  depends_on = [docker_container.postgres]
}

# Outputs
output "printers_service_url" {
  value = "http://localhost:8000"
}

output "monitoring_service_url" {
  value = "http://localhost:8001"
}

output "calibration_service_url" {
  value = "http://localhost:8002"
}

output "postgres_connection" {
  value = "postgresql://postgres:postgres@localhost:5432/printing_db"
}
