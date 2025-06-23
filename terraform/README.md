# Printing Domain Infrastructure

This directory contains Terraform configuration for deploying the Printing Domain microservices.

## Prerequisites

- Docker and Docker Compose
- Terraform 1.0+
- Docker Terraform provider configured

## Structure

- `main.tf`: Main Terraform configuration
- `variables.tf`: Input variables
- `outputs.tf`: Output values

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the execution plan:
   ```bash
   terraform plan
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

4. To destroy all resources:
   ```bash
   terraform destroy
   ```

## Services

The following services will be deployed:

1. **PostgreSQL Database**
   - Port: 5432
   - Database: printing_db
   - Username: postgres
   - Password: postgres

2. **Printers Service**
   - Port: 8000
   - Docs: http://localhost:8000/docs

3. **Monitoring Service**
   - Port: 8001
   - Docs: http://localhost:8001/docs

4. **Calibration Service**
   - Port: 8002
   - Docs: http://localhost:8002/docs

## Variables

| Name | Description | Default |
|------|-------------|---------|
| environment | Environment (dev, staging, prod) | dev |
| postgres_user | PostgreSQL username | postgres |
| postgres_password | PostgreSQL password | postgres |
| postgres_db | PostgreSQL database name | printing_db |

## Outputs

After applying the configuration, the following outputs will be displayed:

- Service URLs
- Database connection details
- Documentation links
