output "services" {
  description = "URLs of the deployed services"
  value = {
    printers_service = {
      url = "http://localhost:8000"
      docs = "http://localhost:8000/docs"
    }
    monitoring_service = {
      url = "http://localhost:8001"
      docs = "http://localhost:8001/docs"
    }
    calibration_service = {
      url = "http://localhost:8002"
      docs = "http://localhost:8002/docs"
    }
    postgres = {
      host = "localhost"
      port = 5432
      database = var.postgres_db
      username = var.postgres_user
    }
  }
}

output "documentation" {
  description = "Documentation links"
  value = {
    fastapi_docs = "https://fastapi.tiangolo.com/"
    docker_docs = "https://docs.docker.com/"
    terraform_docs = "https://www.terraform.io/docs"
  }
}
