# PrintDM - Infraestructura AWS con ALB e IPs Elásticas

Esta configuración de Terraform despliega el sistema PrintDM en AWS con las siguientes características:

## 🏗️ Arquitectura

### Componentes Principales

1. **VPC y Redes**
   - VPC personalizada con subnets públicas y privadas
   - Internet Gateway para acceso público
   - NAT Gateway para acceso a internet desde subnets privadas

2. **Application Load Balancer (ALB)**
   - Distribuye el tráfico entre los servicios
   - Health checks automáticos
   - Listeners configurados para cada servicio

3. **IPs Elásticas**
   - 3 IPs elásticas asignadas (una por servicio)
   - IPs fijas que no cambian al reiniciar instancias

4. **ECS Fargate**
   - Servicios ejecutándose en contenedores sin servidor
   - Auto-scaling configurado
   - Logs centralizados en CloudWatch

5. **RDS PostgreSQL**
   - Base de datos gestionada por AWS
   - Backup automático configurado
   - Alta disponibilidad en producción

## 📋 Recursos Creados

### Redes
- VPC con CIDR `10.0.0.0/16`
- 2 subnets públicas (para ALB y NAT Gateway)
- 2 subnets privadas (para servicios ECS)
- Route tables configuradas

### Seguridad
- Security Groups para ALB, servicios y base de datos
- IAM roles para ECS
- Políticas de acceso configuradas

### Servicios
- **Printers Service**: Puerto 8000
- **Monitoring Service**: Puerto 8001
- **Calibration Service**: Puerto 8002

### Base de Datos
- RDS PostgreSQL 13.7
- Instancia t3.micro (desarrollo)
- Storage gp2 con auto-scaling

## 🚀 Despliegue

### Prerrequisitos

1. **AWS CLI configurado**
   ```bash
   aws configure
   ```

2. **Terraform instalado**
   ```bash
   # Verificar versión
   terraform --version
   ```

3. **ECR configurado**
   ```bash
   # Crear repositorio ECR
   aws ecr create-repository --repository-name printdm
   ```

### Pasos de Despliegue

1. **Configurar variables**
   ```bash
   cd terraform/aws
   cp terraform.tfvars.example terraform.tfvars
   # Editar terraform.tfvars con tus valores
   ```

2. **Inicializar Terraform**
   ```bash
   terraform init
   ```

3. **Revisar el plan**
   ```bash
   terraform plan
   ```

4. **Aplicar la configuración**
   ```bash
   terraform apply
   ```

5. **Verificar el despliegue**
   ```bash
   terraform output
   ```

## 🔧 Configuración

### Variables Importantes

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `aws_region` | Región de AWS | `us-east-1` |
| `environment` | Ambiente (dev/staging/prod) | `dev` |
| `db_password` | Contraseña de PostgreSQL | Requerida |
| `ecr_repository_url` | URL del repositorio ECR | Requerida |

### Puertos y URLs

- **ALB DNS**: `http://[alb-dns-name]`
- **Printers Service**: `http://[alb-dns-name]:8000`
- **Monitoring Service**: `http://[alb-dns-name]:8001`
- **Calibration Service**: `http://[alb-dns-name]:8002`
- **Documentación**: `http://[alb-dns-name]:[puerto]/docs`

## 📊 Monitoreo

### CloudWatch Logs
- Logs centralizados para cada servicio
- Retención configurable por ambiente
- Búsqueda y filtrado avanzado

### Health Checks
- ALB verifica `/health` cada 30 segundos
- Threshold: 2 intentos fallidos antes de marcar como unhealthy
- Timeout: 5 segundos

### Métricas
- CPU y memoria de ECS
- Latencia del ALB
- Conexiones de base de datos

## 🔒 Seguridad

### Security Groups
- **ALB**: Solo puertos 80 y 443 desde internet
- **Servicios**: Solo comunicación interna
- **Base de datos**: Solo desde servicios ECS

### IAM
- Roles mínimos necesarios
- Políticas específicas por servicio
- Sin credenciales hardcodeadas

## 💰 Costos Estimados

### Desarrollo (us-east-1)
- **ALB**: ~$16/mes
- **NAT Gateway**: ~$45/mes
- **RDS t3.micro**: ~$12/mes
- **ECS Fargate**: ~$15/mes
- **IPs Elásticas**: ~$3/mes
- **Total estimado**: ~$91/mes

### Producción
- **RDS t3.small**: ~$25/mes
- **ECS con auto-scaling**: ~$50-100/mes
- **Total estimado**: ~$150-200/mes

## 🛠️ Mantenimiento

### Actualizaciones
```bash
# Actualizar configuración
terraform plan
terraform apply

# Actualizar imágenes
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [ecr-url]
docker push [ecr-url]:latest
```

### Escalado
```bash
# Cambiar número de instancias
terraform apply -var="service_desired_count=3"
```

### Backup
- RDS: Backup automático diario
- ECR: Imágenes versionadas
- Terraform state: Usar backend remoto

## 🚨 Troubleshooting

### Servicios no responden
1. Verificar health checks en ALB
2. Revisar logs en CloudWatch
3. Verificar security groups

### Base de datos no accesible
1. Verificar endpoint de RDS
2. Revisar security group de base de datos
3. Verificar credenciales

### IPs Elásticas no asignadas
1. Verificar que las IPs estén asociadas
2. Revisar configuración de red
3. Verificar límites de AWS

## 📝 Notas Importantes

1. **Cambiar contraseñas**: Usar contraseñas seguras en producción
2. **Limitar acceso SSH**: Restringir `allowed_ssh_cidr` en producción
3. **Backup de state**: Usar backend remoto para el estado de Terraform
4. **Monitoreo**: Configurar alertas en CloudWatch
5. **Costos**: Revisar regularmente los costos en AWS Cost Explorer

## 🔗 Enlaces Útiles

- [Documentación AWS ECS](https://docs.aws.amazon.com/ecs/)
- [Documentación AWS ALB](https://docs.aws.amazon.com/elasticloadbalancing/)
- [Documentación AWS RDS](https://docs.aws.amazon.com/rds/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) 