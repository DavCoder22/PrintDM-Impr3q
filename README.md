# Printing Domain Microservices

A distributed system for managing printing operations, monitoring, and calibration services.

## Project Structure

```
printing-domain/
├── services/                    # Microservices
│   ├── printers-service/       # Printers management service
│   ├── monitoring-service/     # Real-time monitoring service
│   └── calibration-service/    # Printer calibration service
├── terraform/                  # Infrastructure as Code
├── scripts/                    # Utility scripts
└── docs/                       # Documentation
```

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+
- Terraform 1.0+

## Getting Started

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. Access the services:
   - Printers Service: http://localhost:8000
   - Monitoring Service: http://localhost:8001
   - Calibration Service: http://localhost:8002

## Development

### Setting Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r services/<service-name>/requirements-dev.txt
   ```

### Running Tests

Run tests for all services:
```bash
./scripts/run_tests.sh
```

## Infrastructure

### Terraform

To initialize and apply Terraform configurations:

```bash
cd terraform
terraform init
terraform apply
```

## API Documentation

Each service provides its own OpenAPI documentation at `/docs` endpoint when running locally.

## License

MIT License
