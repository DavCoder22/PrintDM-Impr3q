# Plan de Pruebas de Funcionamiento - PrintDM

## 1. Resumen Ejecutivo

Este documento describe el plan de pruebas de funcionamiento para el sistema PrintDM (Printing Domain Management), un sistema distribuido para la gestión de impresoras 3D que consta de tres microservicios principales.

### 1.1 Objetivos de las Pruebas

- Verificar el funcionamiento correcto de todos los microservicios
- Validar la integración entre servicios
- Comprobar la escalabilidad y rendimiento del sistema
- Asegurar la robustez ante fallos
- Validar la documentación de APIs (Swagger)

### 1.2 Alcance

- **Printers Service**: Gestión de impresoras y especificaciones
- **Monitoring Service**: Monitoreo de trabajos de impresión y estado
- **Calibration Service**: Gestión de calibración automática
- **Infraestructura**: Docker Compose y Terraform
- **Integración**: Comunicación entre microservicios

## 2. Entorno de Pruebas

### 2.1 Entorno Local (Docker Compose)

```bash
# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### 2.2 Entorno Terraform

```bash
# Inicializar Terraform
cd terraform
terraform init

# Aplicar configuración
terraform apply -auto-approve

# Verificar recursos
terraform show
```

### 2.3 URLs de Acceso

- **Printers Service**: http://localhost:8000
- **Monitoring Service**: http://localhost:8002
- **Calibration Service**: http://localhost:8001
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050

## 3. Pruebas Unitarias

### 3.1 Printers Service

#### 3.1.1 Pruebas de Endpoints

| Endpoint | Método | Descripción | Casos de Prueba |
|----------|--------|-------------|-----------------|
| `/health` | GET | Verificar salud del servicio | - Servicio funcionando<br>- Respuesta correcta |
| `/printers` | GET | Listar impresoras | - Lista vacía<br>- Lista con impresoras |
| `/printers` | POST | Crear impresora | - Datos válidos<br>- Datos inválidos<br>- IP duplicada |
| `/printers/{id}` | GET | Obtener impresora | - ID válido<br>- ID inexistente |
| `/printers/{id}/volume` | PUT | Actualizar volumen | - Volumen válido<br>- Volumen negativo |
| `/printers/{id}/calibrate` | POST | Calibrar impresora | - Calibración exitosa<br>- ID inexistente |
| `/printers/{id}/info` | GET | Información detallada | - Información completa<br>- ID inexistente |

#### 3.1.2 Pruebas de Validación

- Validación de dirección IP
- Validación de especificaciones técnicas
- Validación de estados de impresora
- Validación de volumen de impresión

### 3.2 Monitoring Service

#### 3.2.1 Pruebas de Endpoints

| Endpoint | Método | Descripción | Casos de Prueba |
|----------|--------|-------------|-----------------|
| `/health` | GET | Verificar salud | - Servicio funcionando |
| `/monitoring/status` | GET | Estado del sistema | - Estado operacional |
| `/monitoring/alerts` | POST | Crear alerta | - Alerta válida<br>- Datos inválidos |
| `/monitoring/alerts` | GET | Listar alertas | - Filtrado por estado |
| `/monitoring/metrics` | POST | Registrar métrica | - Métrica válida |
| `/monitoring/metrics` | GET | Consultar métricas | - Filtros aplicados |
| `/print-jobs` | POST | Crear trabajo | - Trabajo válido |
| `/print-jobs/{id}` | GET | Obtener trabajo | - ID válido<br>- ID inexistente |
| `/print-jobs/{id}` | PUT | Actualizar trabajo | - Actualización válida |
| `/print-jobs/{id}/start` | POST | Iniciar trabajo | - Inicio exitoso |
| `/print-jobs/{id}/pause` | POST | Pausar trabajo | - Pausa exitosa |
| `/print-jobs/{id}/resume` | POST | Reanudar trabajo | - Reanudación exitosa |
| `/print-jobs/{id}/cancel` | POST | Cancelar trabajo | - Cancelación exitosa |

#### 3.2.2 Pruebas de Monitoreo

- Monitoreo de trabajos en tiempo real
- Detección de timeouts
- Gestión de estados de impresora
- Sistema de alertas

### 3.3 Calibration Service

#### 3.3.1 Pruebas de Endpoints

| Endpoint | Método | Descripción | Casos de Prueba |
|----------|--------|-------------|-----------------|
| `/health` | GET | Verificar salud | - Servicio funcionando |
| `/calibration/start` | POST | Iniciar calibración | - Calibración válida |
| `/calibration/{id}` | GET | Estado calibración | - ID válido<br>- ID inexistente |
| `/calibration/printer/{id}` | GET | Historial calibraciones | - Historial completo |
| `/calibration/profiles` | POST | Crear perfil | - Perfil válido |
| `/calibration/profiles/{id}` | GET | Obtener perfil | - ID válido |
| `/calibration/profiles` | GET | Listar perfiles | - Filtros aplicados |
| `/printers/{id}/print-completed` | POST | Notificar impresión | - Notificación válida |
| `/printers/{id}/calibration-status` | GET | Estado calibración | - Estado actual |
| `/printers/{id}/calibrate` | POST | Calibración manual | - Calibración exitosa |

#### 3.3.2 Pruebas de Calibración

- Contadores de impresión
- Alertas automáticas (después de 3 impresiones)
- Perfiles de calibración
- Historial de calibraciones

## 4. Pruebas de Integración

### 4.1 Flujo de Trabajo Completo

#### 4.1.1 Escenario: Impresión Completa

1. **Crear Impresora**
   ```bash
   POST /printers
   {
     "name": "Test Printer",
     "model": "Ender 3",
     "ip_address": "192.168.1.100",
     "location": "Lab A"
   }
   ```

2. **Crear Trabajo de Impresión**
   ```bash
   POST /print-jobs
   {
     "printer_id": "1",
     "file_name": "test.gcode",
     "file_size": 1024,
     "estimated_duration": 3600
   }
   ```

3. **Iniciar Trabajo**
   ```bash
   POST /print-jobs/{job_id}/start
   ```

4. **Monitorear Progreso**
   ```bash
   GET /print-jobs/{job_id}
   ```

5. **Completar Trabajo**
   ```bash
   PUT /print-jobs/{job_id}
   {
     "status": "completed",
     "progress": 100.0
   }
   ```

6. **Notificar Calibración**
   ```bash
   POST /printers/{printer_id}/print-completed
   {
     "volume_cm3": 50.0
   }
   ```

#### 4.1.2 Escenario: Calibración Automática

1. **Realizar 3 impresiones** (repetir flujo anterior)
2. **Verificar alerta de calibración**
3. **Realizar calibración**
4. **Verificar reset de contador**

### 4.2 Pruebas de Comunicación entre Servicios

- Verificar que el Monitoring Service puede comunicarse con Printers Service
- Verificar que el Calibration Service puede comunicarse con Printers Service
- Verificar que las alertas se propagan correctamente
- Verificar la sincronización de estados

## 5. Pruebas de Rendimiento

### 5.1 Carga de Trabajo

- **Concurrente**: 10 trabajos de impresión simultáneos
- **Volumen**: 100 impresoras registradas
- **Duración**: 30 minutos de prueba continua

### 5.2 Métricas a Medir

- Tiempo de respuesta de APIs
- Uso de memoria por servicio
- Uso de CPU por servicio
- Latencia de red entre servicios
- Throughput de base de datos

### 5.3 Límites Esperados

- Tiempo de respuesta < 500ms para 95% de requests
- Uso de memoria < 512MB por servicio
- Uso de CPU < 50% por servicio
- Disponibilidad > 99.9%

## 6. Pruebas de Robustez

### 6.1 Pruebas de Fallo

#### 6.1.1 Fallo de Servicio Individual

1. Detener Printers Service
2. Verificar que Monitoring Service maneja el fallo
3. Verificar que Calibration Service maneja el fallo
4. Reiniciar Printers Service
5. Verificar recuperación automática

#### 6.1.2 Fallo de Base de Datos

1. Detener PostgreSQL
2. Verificar comportamiento de servicios
3. Reiniciar PostgreSQL
4. Verificar recuperación de datos

#### 6.1.3 Fallo de Red

1. Simular latencia alta entre servicios
2. Verificar timeouts configurados
3. Verificar reintentos automáticos

### 6.2 Pruebas de Recuperación

- Recuperación automática después de fallos
- Persistencia de datos críticos
- Sincronización de estados después de recuperación

## 7. Pruebas de Seguridad

### 7.1 Validación de Entrada

- Inyección SQL (aunque usa ORM)
- XSS en campos de texto
- Validación de tipos de datos
- Límites de tamaño de archivo

### 7.2 Autenticación y Autorización

- Verificar endpoints protegidos (futuro)
- Validación de tokens (futuro)
- Control de acceso por roles (futuro)

## 8. Pruebas de Documentación

### 8.1 Swagger/OpenAPI

- Verificar que todos los endpoints están documentados
- Verificar que los modelos están definidos
- Verificar que los ejemplos son correctos
- Verificar que las descripciones son claras

### 8.2 Documentación de Usuario

- Verificar que el README está actualizado
- Verificar que los comandos de instalación funcionan
- Verificar que los ejemplos de uso son correctos

## 9. Scripts de Automatización

### 9.1 Script de Pruebas Básicas

```bash
# Ejecutar pruebas básicas
python scripts/test_services.py
```

### 9.2 Script de Pruebas de Carga

```bash
# Ejecutar pruebas de carga
python scripts/load_test.py
```

### 9.3 Script de Pruebas de Integración

```bash
# Ejecutar pruebas de integración
python scripts/integration_test.py
```

## 10. Criterios de Aceptación

### 10.1 Funcionalidad

- [ ] Todos los endpoints responden correctamente
- [ ] La integración entre servicios funciona
- [ ] Los flujos de trabajo completos funcionan
- [ ] La documentación Swagger está completa

### 10.2 Rendimiento

- [ ] Tiempo de respuesta < 500ms (95%)
- [ ] Uso de memoria < 512MB por servicio
- [ ] Disponibilidad > 99.9% durante pruebas

### 10.3 Robustez

- [ ] Recuperación automática después de fallos
- [ ] Manejo correcto de errores
- [ ] Persistencia de datos críticos

### 10.4 Documentación

- [ ] Swagger completo y actualizado
- [ ] README actualizado
- [ ] Ejemplos de uso funcionando

## 11. Reporte de Pruebas

### 11.1 Plantilla de Reporte

```markdown
# Reporte de Pruebas - PrintDM

## Fecha: [FECHA]
## Versión: [VERSION]
## Entorno: [ENTORNO]

## Resumen
- Total de pruebas: [NUMERO]
- Exitosas: [NUMERO]
- Fallidas: [NUMERO]
- Tasa de éxito: [PORCENTAJE]%

## Detalles por Servicio

### Printers Service
- Pruebas unitarias: [X/Y] exitosas
- Pruebas de integración: [X/Y] exitosas
- Tiempo de respuesta promedio: [TIEMPO]ms

### Monitoring Service
- Pruebas unitarias: [X/Y] exitosas
- Pruebas de integración: [X/Y] exitosas
- Tiempo de respuesta promedio: [TIEMPO]ms

### Calibration Service
- Pruebas unitarias: [X/Y] exitosas
- Pruebas de integración: [X/Y] exitosas
- Tiempo de respuesta promedio: [TIEMPO]ms

## Problemas Encontrados
1. [DESCRIPCION DEL PROBLEMA]
2. [DESCRIPCION DEL PROBLEMA]

## Recomendaciones
1. [RECOMENDACION]
2. [RECOMENDACION]

## Conclusión
[CONCLUSION GENERAL]
```

## 12. Mantenimiento del Plan

### 12.1 Actualizaciones

- Revisar y actualizar el plan cada 2 semanas
- Agregar nuevas pruebas cuando se añadan funcionalidades
- Actualizar criterios de aceptación según necesidades

### 12.2 Mejoras Continuas

- Analizar resultados de pruebas para identificar mejoras
- Optimizar scripts de automatización
- Mejorar cobertura de pruebas

---

**Versión del Plan**: 1.0  
**Última Actualización**: [FECHA]  
**Responsable**: Equipo de Desarrollo PrintDM 