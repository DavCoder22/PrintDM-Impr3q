#!/bin/bash

# Script de Despliegue y Pruebas Automatizadas - PrintDM
# Este script despliega el sistema usando Docker Compose o Terraform y ejecuta pruebas

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
SERVICES=("printers-service" "monitoring-service" "calibration-service")
PORTS=(8000 8002 8001)
HEALTH_ENDPOINTS=("/health" "/health" "/health")

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para mostrar ayuda
show_help() {
    echo "Script de Despliegue y Pruebas - PrintDM"
    echo ""
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  -m, --method METHOD    Método de despliegue (docker-compose|terraform|both)"
    echo "  -t, --test-only        Solo ejecutar pruebas (no desplegar)"
    echo "  -c, --clean            Limpiar recursos antes del despliegue"
    echo "  -v, --verbose          Modo verbose"
    echo "  -h, --help             Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 -m docker-compose   # Desplegar con Docker Compose"
    echo "  $0 -m terraform        # Desplegar con Terraform"
    echo "  $0 -m both             # Desplegar con ambos métodos"
    echo "  $0 -t                  # Solo ejecutar pruebas"
    echo "  $0 -c -m docker-compose # Limpiar y desplegar con Docker Compose"
}

# Variables por defecto
METHOD="docker-compose"
TEST_ONLY=false
CLEAN=false
VERBOSE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--method)
            METHOD="$2"
            shift 2
            ;;
        -t|--test-only)
            TEST_ONLY=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Función para verificar prerequisitos
check_prerequisites() {
    log "Verificando prerequisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado"
        exit 1
    fi
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado"
        exit 1
    fi
    
    # Verificar curl
    if ! command -v curl &> /dev/null; then
        error "curl no está instalado"
        exit 1
    fi
    
    success "Todos los prerequisitos están instalados"
}

# Función para limpiar recursos
clean_resources() {
    log "Limpiando recursos existentes..."
    
    # Limpiar Docker Compose
    if docker-compose ps -q | grep -q .; then
        log "Deteniendo servicios de Docker Compose..."
        docker-compose down -v
    fi
    
    # Limpiar Terraform
    if [ -d "terraform" ] && [ -f "terraform/terraform.tfstate" ]; then
        log "Limpiando recursos de Terraform..."
        cd terraform
        terraform destroy -auto-approve || true
        cd ..
    fi
    
    # Limpiar imágenes Docker
    log "Limpiando imágenes Docker no utilizadas..."
    docker image prune -f
    
    success "Limpieza completada"
}

# Función para desplegar con Docker Compose
deploy_docker_compose() {
    log "Desplegando con Docker Compose..."
    
    # Construir imágenes
    log "Construyendo imágenes..."
    docker-compose build --no-cache
    
    # Iniciar servicios
    log "Iniciando servicios..."
    docker-compose up -d
    
    success "Despliegue con Docker Compose completado"
}

# Función para desplegar con Terraform
deploy_terraform() {
    log "Desplegando con Terraform..."
    
    cd terraform
    
    # Inicializar Terraform
    log "Inicializando Terraform..."
    terraform init
    
    # Aplicar configuración
    log "Aplicando configuración de Terraform..."
    terraform apply -auto-approve
    
    cd ..
    
    success "Despliegue con Terraform completado"
}

# Función para esperar a que los servicios estén listos
wait_for_services() {
    log "Esperando a que los servicios estén listos..."
    
    for i in "${!SERVICES[@]}"; do
        service="${SERVICES[$i]}"
        port="${PORTS[$i]}"
        endpoint="${HEALTH_ENDPOINTS[$i]}"
        
        log "Esperando servicio $service en puerto $port..."
        
        # Esperar hasta 60 segundos por servicio
        for attempt in {1..60}; do
            if curl -s -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
                success "Servicio $service está listo"
                break
            fi
            
            if [ $attempt -eq 60 ]; then
                error "Servicio $service no está respondiendo después de 60 segundos"
                return 1
            fi
            
            sleep 1
        done
    done
    
    success "Todos los servicios están listos"
}

# Función para ejecutar pruebas básicas
run_basic_tests() {
    log "Ejecutando pruebas básicas..."
    
    # Verificar endpoints de salud
    for i in "${!SERVICES[@]}"; do
        service="${SERVICES[$i]}"
        port="${PORTS[$i]}"
        endpoint="${HEALTH_ENDPOINTS[$i]}"
        
        log "Probando endpoint de salud de $service..."
        response=$(curl -s "http://localhost:$port$endpoint")
        
        if echo "$response" | grep -q '"status":"ok"'; then
            success "Endpoint de salud de $service responde correctamente"
        else
            error "Endpoint de salud de $service no responde correctamente"
            return 1
        fi
    done
    
    success "Pruebas básicas completadas"
}

# Función para ejecutar pruebas comprehensivas
run_comprehensive_tests() {
    log "Ejecutando pruebas comprehensivas..."
    
    # Verificar que el script de pruebas existe
    if [ ! -f "scripts/comprehensive_test_suite.py" ]; then
        warning "Script de pruebas comprehensivas no encontrado, ejecutando pruebas básicas"
        run_basic_tests
        return
    fi
    
    # Instalar dependencias si es necesario
    if ! python3 -c "import requests" 2>/dev/null; then
        log "Instalando dependencias de Python..."
        pip3 install requests
    fi
    
    # Ejecutar pruebas comprehensivas
    log "Ejecutando suite de pruebas comprehensiva..."
    python3 scripts/comprehensive_test_suite.py
    
    if [ $? -eq 0 ]; then
        success "Pruebas comprehensivas completadas exitosamente"
    else
        error "Algunas pruebas comprehensivas fallaron"
        return 1
    fi
}

# Función para mostrar información del sistema
show_system_info() {
    log "Información del sistema desplegado:"
    echo ""
    echo "🌐 URLs de acceso:"
    echo "  - Printers Service:     http://localhost:8000"
    echo "  - Monitoring Service:   http://localhost:8002"
    echo "  - Calibration Service:  http://localhost:8001"
    echo "  - PostgreSQL:           localhost:5432"
    echo "  - pgAdmin:              http://localhost:5050"
    echo ""
    echo "📚 Documentación API:"
    echo "  - Printers Service:     http://localhost:8000/docs"
    echo "  - Monitoring Service:   http://localhost:8002/docs"
    echo "  - Calibration Service:  http://localhost:8001/docs"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "  - Ver logs:             docker-compose logs -f"
    echo "  - Detener servicios:    docker-compose down"
    echo "  - Reiniciar servicios:  docker-compose restart"
    echo ""
}

# Función para generar reporte
generate_report() {
    log "Generando reporte de despliegue..."
    
    report_file="deployment_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "Reporte de Despliegue - PrintDM"
        echo "Fecha: $(date)"
        echo "Método: $METHOD"
        echo ""
        echo "Estado de servicios:"
        docker-compose ps
        echo ""
        echo "Logs recientes:"
        docker-compose logs --tail=20
        echo ""
        echo "Uso de recursos:"
        docker stats --no-stream
    } > "$report_file"
    
    success "Reporte generado: $report_file"
}

# Función principal
main() {
    echo "🚀 Script de Despliegue y Pruebas - PrintDM"
    echo "=========================================="
    echo ""
    
    # Verificar prerequisitos
    check_prerequisites
    
    # Limpiar si se solicita
    if [ "$CLEAN" = true ]; then
        clean_resources
    fi
    
    # Desplegar si no es solo pruebas
    if [ "$TEST_ONLY" = false ]; then
        case $METHOD in
            "docker-compose")
                deploy_docker_compose
                ;;
            "terraform")
                deploy_terraform
                ;;
            "both")
                deploy_docker_compose
                deploy_terraform
                ;;
            *)
                error "Método de despliegue inválido: $METHOD"
                exit 1
                ;;
        esac
        
        # Esperar a que los servicios estén listos
        wait_for_services
        
        # Mostrar información del sistema
        show_system_info
    fi
    
    # Ejecutar pruebas
    log "Iniciando ejecución de pruebas..."
    
    # Pruebas básicas
    run_basic_tests
    
    # Pruebas comprehensivas
    run_comprehensive_tests
    
    # Generar reporte
    generate_report
    
    echo ""
    success "🎉 Proceso completado exitosamente!"
    echo ""
    log "El sistema está listo para usar. Consulta la documentación en los endpoints /docs"
}

# Ejecutar función principal
main "$@" 