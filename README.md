# PrintDM - Distributed Printing Management System

A distributed system for managing 3D printers, monitoring print jobs, and handling automatic calibration.

## Project Structure

```
PrintDM-Impr3q/
├── services/                    # Microservices
│   ├── printers-service/       # Printers management and specifications
│   ├── monitoring-service/     # Print job monitoring and status management
│   └── calibration-service/    # Automatic calibration management
├── terraform/                  # Infrastructure as Code
├── scripts/                    # Utility scripts
├── requirements.txt            # Main project dependencies
├── requirements-dev.txt        # Development dependencies
└── docker-compose.yml          # Docker Compose configuration
```

## Dependency Management

This project uses a centralized dependency management system:

- `requirements.txt`: Contains all production dependencies for the entire project
- `requirements-dev.txt`: Contains additional development dependencies (testing, linting, etc.)

### Setting Up the Environment

1. Create and activate a virtual environment:


   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```


2. Install dependencies:

   ```bash
   # For production
   pip install -r requirements.txt
   
   # For development (includes testing and linting tools)
   pip install -r requirements-dev.txt
   ```

### Testing

### Pruebas Automatizadas

El sistema incluye un plan de pruebas de funcionamiento completo:

```bash
# Ejecutar pruebas básicas
python scripts/test_services.py

# Ejecutar suite comprehensiva de pruebas
make test-comprehensive

# Desplegar y ejecutar todas las pruebas
make deploy-test-docker
```

### Tipos de Pruebas

- ✅ **Pruebas Unitarias**: Endpoints individuales y validación
- ✅ **Pruebas de Integración**: Comunicación entre servicios
- ✅ **Pruebas de Rendimiento**: Carga y métricas
- ✅ **Pruebas de Robustez**: Manejo de errores y recuperación

### Reportes de Pruebas

Los scripts generan reportes detallados con:
- Estado de cada prueba
- Métricas de rendimiento
- Logs de errores
- Recomendaciones de mejora

Para más detalles, consulta [PLAN_PRUEBAS.md](PLAN_PRUEBAS.md) y [EVALUACION_MICROSERVICIOS.md](EVALUACION_MICROSERVICIOS.md).

## Services Overview

### 1. Printers Service

- Manages printer information and specifications
- Tracks print volume and usage
- Provides printer status and capabilities

**Port:** 8000

### 2. Calibration Service

- Tracks print counts
- Manages automatic calibration alerts (after 3 prints)
- Handles calibration history

**Port:** 8001

### 3. Monitoring Service

- Manages print jobs and their status
- Handles printer status updates
- Provides real-time monitoring of print jobs
- Integrates with calibration service for alerts

**Port:** 8002

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+

## Getting Started

### Opción 1: Despliegue Rápido con Docker Compose

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. Access the services:

   - **Printers Service:** [http://localhost:8000](http://localhost:8000)
   - **Monitoring Service:** [http://localhost:8002](http://localhost:8002)
   - **Calibration Service:** [http://localhost:8001](http://localhost:8001)
   - **PostgreSQL:** `localhost:5433` (configurado para evitar conflictos)
   - **pgAdmin:** [http://localhost:5050](http://localhost:5050) (admin@example.com/admin)

### Solución de Conflictos de Puertos

Si encuentras errores de puertos ocupados:

1. **Verificar puertos en uso:**
   ```bash
   # Windows
   netstat -ano | findstr :5432
   
   # Linux/Mac
   lsof -i :5432
   ```

2. **Cambiar puerto de PostgreSQL en docker-compose.yml:**
   ```yaml
   postgres:
     ports:
       - "5434:5432"  # Cambiar 5434 por cualquier puerto libre
   ```

3. **Actualizar variables de entorno si es necesario:**
   ```yaml
   environment:
     - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/printing_db
   ```
   *Nota: El puerto interno (5432) no cambia, solo el externo.*

### Opción 2: Despliegue Automatizado con Pruebas

```bash
# Desplegar con Docker Compose y ejecutar pruebas
make deploy-test-docker

# Desplegar con Terraform y ejecutar pruebas
make deploy-test-terraform

# Solo ejecutar pruebas (sin desplegar)
make test-only

# Limpiar y desplegar
make clean-deploy
```

### Opción 3: Despliegue Manual con Terraform (Local)

```bash
# Inicializar Terraform
cd terraform && terraform init

# Aplicar configuración
terraform apply -auto-approve

# Verificar estado
terraform show
```

### Opción 4: Despliegue en AWS con ALB e IPs Elásticas

```bash
# Configurar AWS CLI
aws configure

# Crear repositorio ECR
aws ecr create-repository --repository-name printdm

# Configurar variables
cd terraform/aws
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores

# Desplegar en AWS
terraform init
terraform plan
terraform apply
```

**Características de AWS:**
- ✅ **Application Load Balancer (ALB)** para distribución de tráfico
- ✅ **3 IPs Elásticas** asignadas (una por servicio)
- ✅ **ECS Fargate** para ejecución sin servidor
- ✅ **RDS PostgreSQL** gestionado
- ✅ **CloudWatch** para logs y monitoreo
- ✅ **Security Groups** configurados
- ✅ **VPC** personalizada con subnets públicas/privadas

Para más detalles, consulta [terraform/aws/README.md](terraform/aws/README.md).

## Key Features

### Print Job Management

- Create and track print jobs
- Monitor print progress in real-time
- Pause/resume/cancel print jobs
- Automatic timeout detection

### Printer Status

- Real-time status updates
- Automatic calibration alerts
- Print volume tracking
- Detailed printer specifications

### Calibration System

- Automatic calibration alerts after 3 prints
- Calibration history tracking
- Integration with printer status

## API Documentation

Each service provides interactive OpenAPI documentation with comprehensive Swagger documentation:

- **Printers Service API:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Monitoring Service API:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **Calibration Service API:** [http://localhost:8001/docs](http://localhost:8001/docs)

### Documentación Mejorada

Todos los servicios incluyen:
- ✅ Descripciones detalladas de funcionalidades
- ✅ Ejemplos de uso con datos reales
- ✅ Tags organizados por categorías
- ✅ Información de contacto del equipo
- ✅ Documentación de integración entre servicios

## Development

### Setting Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r services/<service-name>/requirements-dev.txt
   ```

### Running Tests

To run tests for a specific service:
```bash
cd services/<service-name>
pytest -v --cov=app tests/
```

To run all tests with coverage:
```bash
./scripts/run_tests.sh
```

## Service Interactions

1. **Starting a Print Job:**
   - Monitoring Service creates a new print job
   - Updates printer status to "printing"
   - Tracks print progress

2. **Print Completion:**
   - Monitoring Service marks job as completed
   - Updates printer status
   - Notifies Calibration Service of print completion

3. **Calibration Alert:**
   - After 3 prints, Calibration Service triggers an alert
   - Updates printer status to "calibration_needed"
   - Monitoring Service shows alert in dashboard

## Environment Variables

### Printers Service

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: info)

### Monitoring Service

- `DATABASE_URL`: PostgreSQL connection string
- `PRINTERS_SERVICE_URL`: URL of Printers Service (default: `http://printers-service:8000`)
- `CALIBRATION_SERVICE_URL`: URL of Calibration Service (default: `http://calibration-service:8000`)
- `LOG_LEVEL`: Logging level (default: info)

### Calibration Service

- `DATABASE_URL`: PostgreSQL connection string
- `PRINTERS_SERVICE_URL`: URL of Printers Service (default: `http://printers-service:8000`)
- `LOG_LEVEL`: Logging level (default: info)

## Deployment

### Docker Compose


```bash
docker-compose up -d --build
```


### Kubernetes (Optional)

See the `kubernetes/` directory for deployment manifests.

## Evaluación y Documentación

### Documentos de Evaluación

- **[EVALUACION_MICROSERVICIOS.md](EVALUACION_MICROSERVICIOS.md)**: Evaluación completa del sistema
- **[PLAN_PRUEBAS.md](PLAN_PRUEBAS.md)**: Plan detallado de pruebas de funcionamiento

### Estado del Sistema

- ✅ **Microservicios**: Funcionando correctamente
- ✅ **Docker Compose**: Configurado para desarrollo local
- ✅ **Terraform**: Infraestructura como código implementada
- ✅ **Documentación Swagger**: Completa y detallada
- ✅ **Pruebas Automatizadas**: Suite comprehensiva implementada

### Comandos de Evaluación

```bash
# Ver todos los comandos disponibles
make help

# Evaluación completa del sistema
make deploy-test-docker

# Solo ejecutar pruebas
make test-only
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

### Guías de Contribución

- Ejecuta las pruebas antes de hacer commit: `make test-comprehensive`
- Actualiza la documentación si es necesario
- Sigue las convenciones de código establecidas
- Verifica que la integración entre servicios funcione
