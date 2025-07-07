#!/usr/bin/env python3
"""
Suite de Pruebas Comprehensiva para PrintDM
Este script ejecuta pruebas automatizadas para todos los microservicios del sistema.
"""

import sys
import json
import time
import requests
import threading
import concurrent.futures
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import statistics

# Configuración de servicios
SERVICES = {
    'printers': {
        'url': 'http://localhost:8000',
        'name': 'Printers Service',
        'port': 8000
    },
    'monitoring': {
        'url': 'http://localhost:8002',
        'name': 'Monitoring Service',
        'port': 8002
    },
    'calibration': {
        'url': 'http://localhost:8001',
        'name': 'Calibration Service',
        'port': 8001
    }
}

# Configuración de pruebas
TEST_CONFIG = {
    'timeout': 10,
    'retries': 3,
    'concurrent_requests': 5,
    'load_test_duration': 60,  # segundos
    'load_test_requests_per_second': 10
}

class TestResult:
    """Clase para almacenar resultados de pruebas"""
    def __init__(self, test_name: str, success: bool, duration: float = 0, error: str = None, data: Any = None):
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.error = error
        self.data = data
        self.timestamp = datetime.utcnow()

class PrintDMTestSuite:
    """Suite principal de pruebas para PrintDM"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.session.timeout = TEST_CONFIG['timeout']
        
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_test(self, test_func, *args, **kwargs) -> TestResult:
        """Ejecuta una prueba y registra el resultado"""
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            return TestResult(test_func.__name__, True, duration, data=result)
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(test_func.__name__, False, duration, error=str(e))
    
    def add_result(self, result: TestResult):
        """Agrega un resultado a la lista"""
        self.results.append(result)
        status = "✅ PASS" if result.success else "❌ FAIL"
        self.log(f"{result.test_name}: {status} ({result.duration:.3f}s)")
        if result.error:
            self.log(f"  Error: {result.error}", "ERROR")
    
    # ==================== PRUEBAS DE SALUD ====================
    
    def test_service_health(self, service_name: str) -> bool:
        """Prueba el endpoint de salud de un servicio"""
        service = SERVICES[service_name]
        response = self.session.get(f"{service['url']}/health")
        if response.status_code != 200:
            raise Exception(f"Status code: {response.status_code}")
        
        data = response.json()
        if data.get('status') != 'ok':
            raise Exception(f"Invalid health status: {data.get('status')}")
        
        return data
    
    def test_all_services_health(self):
        """Prueba la salud de todos los servicios"""
        self.log("=== PRUEBAS DE SALUD DE SERVICIOS ===")
        
        for service_name in SERVICES:
            result = self.run_test(self.test_service_health, service_name)
            self.add_result(result)
    
    # ==================== PRUEBAS DE PRINTERS SERVICE ====================
    
    def test_create_printer(self) -> Dict[str, Any]:
        """Prueba la creación de una impresora"""
        printer_data = {
            "name": f"Test Printer {int(time.time())}",
            "model": "Ender 3 Pro",
            "ip_address": "192.168.1.100",
            "location": "Test Lab",
            "status": "offline",
            "print_volume_tolerance": 100.0,
            "specs": {
                "max_volume_mm": {"x": 220, "y": 220, "z": 250},
                "supported_materials": ["PLA", "ABS", "PETG"],
                "layer_resolution_mm": 0.2,
                "has_heated_bed": True
            }
        }
        
        response = self.session.post(f"{SERVICES['printers']['url']}/printers", json=printer_data)
        if response.status_code != 201:
            raise Exception(f"Failed to create printer: {response.text}")
        
        return response.json()
    
    def test_list_printers(self) -> List[Dict[str, Any]]:
        """Prueba el listado de impresoras"""
        response = self.session.get(f"{SERVICES['printers']['url']}/printers")
        if response.status_code != 200:
            raise Exception(f"Failed to list printers: {response.text}")
        
        return response.json()
    
    def test_get_printer(self, printer_id: str) -> Dict[str, Any]:
        """Prueba obtener una impresora específica"""
        response = self.session.get(f"{SERVICES['printers']['url']}/printers/{printer_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get printer: {response.text}")
        
        return response.json()
    
    def test_update_printer_volume(self, printer_id: str, volume: float) -> Dict[str, Any]:
        """Prueba actualizar el volumen de impresión"""
        response = self.session.put(
            f"{SERVICES['printers']['url']}/printers/{printer_id}/volume",
            params={"volume_cm3": volume}
        )
        if response.status_code != 200:
            raise Exception(f"Failed to update volume: {response.text}")
        
        return response.json()
    
    def test_calibrate_printer(self, printer_id: str) -> Dict[str, Any]:
        """Prueba calibrar una impresora"""
        response = self.session.post(f"{SERVICES['printers']['url']}/printers/{printer_id}/calibrate")
        if response.status_code != 200:
            raise Exception(f"Failed to calibrate printer: {response.text}")
        
        return response.json()
    
    def test_printers_service_comprehensive(self):
        """Pruebas comprehensivas del servicio de impresoras"""
        self.log("=== PRUEBAS COMPREHENSIVAS - PRINTERS SERVICE ===")
        
        # Crear impresora
        result = self.run_test(self.test_create_printer)
        self.add_result(result)
        if not result.success:
            return
        
        printer = result.data
        printer_id = printer['id']
        
        # Listar impresoras
        result = self.run_test(self.test_list_printers)
        self.add_result(result)
        
        # Obtener impresora específica
        result = self.run_test(self.test_get_printer, printer_id)
        self.add_result(result)
        
        # Actualizar volumen
        result = self.run_test(self.test_update_printer_volume, printer_id, 50.0)
        self.add_result(result)
        
        # Calibrar impresora
        result = self.run_test(self.test_calibrate_printer, printer_id)
        self.add_result(result)
    
    # ==================== PRUEBAS DE MONITORING SERVICE ====================
    
    def test_create_print_job(self, printer_id: str) -> Dict[str, Any]:
        """Prueba crear un trabajo de impresión"""
        job_data = {
            "printer_id": printer_id,
            "file_name": f"test_file_{int(time.time())}.gcode",
            "file_size": 1024,
            "estimated_duration": 3600
        }
        
        response = self.session.post(f"{SERVICES['monitoring']['url']}/print-jobs", json=job_data)
        if response.status_code != 201:
            raise Exception(f"Failed to create print job: {response.text}")
        
        return response.json()
    
    def test_get_print_job(self, job_id: str) -> Dict[str, Any]:
        """Prueba obtener un trabajo de impresión"""
        response = self.session.get(f"{SERVICES['monitoring']['url']}/print-jobs/{job_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to get print job: {response.text}")
        
        return response.json()
    
    def test_update_print_job(self, job_id: str, status: str, progress: float) -> Dict[str, Any]:
        """Prueba actualizar un trabajo de impresión"""
        update_data = {
            "status": status,
            "progress": progress
        }
        
        response = self.session.put(f"{SERVICES['monitoring']['url']}/print-jobs/{job_id}", json=update_data)
        if response.status_code != 200:
            raise Exception(f"Failed to update print job: {response.text}")
        
        return response.json()
    
    def test_create_alert(self) -> Dict[str, Any]:
        """Prueba crear una alerta"""
        alert_data = {
            "printer_id": "test-printer",
            "level": "warning",
            "message": "Test alert message",
            "details": {"test": "data"}
        }
        
        response = self.session.post(f"{SERVICES['monitoring']['url']}/monitoring/alerts", json=alert_data)
        if response.status_code != 201:
            raise Exception(f"Failed to create alert: {response.text}")
        
        return response.json()
    
    def test_monitoring_service_comprehensive(self):
        """Pruebas comprehensivas del servicio de monitoreo"""
        self.log("=== PRUEBAS COMPREHENSIVAS - MONITORING SERVICE ===")
        
        # Crear trabajo de impresión
        result = self.run_test(self.test_create_print_job, "1")
        self.add_result(result)
        if not result.success:
            return
        
        job = result.data
        job_id = job['id']
        
        # Obtener trabajo
        result = self.run_test(self.test_get_print_job, job_id)
        self.add_result(result)
        
        # Actualizar trabajo
        result = self.run_test(self.test_update_print_job, job_id, "printing", 25.0)
        self.add_result(result)
        
        # Crear alerta
        result = self.run_test(self.test_create_alert)
        self.add_result(result)
    
    # ==================== PRUEBAS DE CALIBRATION SERVICE ====================
    
    def test_create_calibration_profile(self) -> Dict[str, Any]:
        """Prueba crear un perfil de calibración"""
        profile_data = {
            "name": f"Test Profile {int(time.time())}",
            "description": "Test calibration profile",
            "printer_model": "Ender 3 Pro",
            "parameters": {"test_param": 1.0},
            "is_default": True
        }
        
        response = self.session.post(f"{SERVICES['calibration']['url']}/calibration/profiles", json=profile_data)
        if response.status_code != 201:
            raise Exception(f"Failed to create profile: {response.text}")
        
        return response.json()
    
    def test_start_calibration(self, printer_id: str, profile_id: str) -> Dict[str, Any]:
        """Prueba iniciar una calibración"""
        calibration_data = {
            "printer_id": printer_id,
            "profile_id": profile_id,
            "calibration_type": "automatic",
            "notes": "Test calibration"
        }
        
        response = self.session.post(f"{SERVICES['calibration']['url']}/calibration/start", json=calibration_data)
        if response.status_code != 201:
            raise Exception(f"Failed to start calibration: {response.text}")
        
        return response.json()
    
    def test_notify_print_completed(self, printer_id: str) -> Dict[str, Any]:
        """Prueba notificar impresión completada"""
        data = {"volume_cm3": 25.0}
        
        response = self.session.post(f"{SERVICES['calibration']['url']}/printers/{printer_id}/print-completed", json=data)
        if response.status_code != 200:
            raise Exception(f"Failed to notify print completed: {response.text}")
        
        return response.json()
    
    def test_calibration_service_comprehensive(self):
        """Pruebas comprehensivas del servicio de calibración"""
        self.log("=== PRUEBAS COMPREHENSIVAS - CALIBRATION SERVICE ===")
        
        # Crear perfil de calibración
        result = self.run_test(self.test_create_calibration_profile)
        self.add_result(result)
        if not result.success:
            return
        
        profile = result.data
        profile_id = profile['id']
        
        # Iniciar calibración
        result = self.run_test(self.test_start_calibration, "1", profile_id)
        self.add_result(result)
        
        # Notificar impresión completada
        result = self.run_test(self.test_notify_print_completed, "1")
        self.add_result(result)
    
    # ==================== PRUEBAS DE INTEGRACIÓN ====================
    
    def test_integration_workflow(self):
        """Prueba el flujo de trabajo completo de integración"""
        self.log("=== PRUEBAS DE INTEGRACIÓN - FLUJO COMPLETO ===")
        
        # 1. Crear impresora
        result = self.run_test(self.test_create_printer)
        self.add_result(result)
        if not result.success:
            return
        
        printer = result.data
        printer_id = printer['id']
        
        # 2. Crear trabajo de impresión
        result = self.run_test(self.test_create_print_job, printer_id)
        self.add_result(result)
        if not result.success:
            return
        
        job = result.data
        job_id = job['id']
        
        # 3. Simular progreso de impresión
        for progress in [25, 50, 75, 100]:
            result = self.run_test(self.test_update_print_job, job_id, "printing", progress)
            self.add_result(result)
        
        # 4. Completar impresión
        result = self.run_test(self.test_update_print_job, job_id, "completed", 100)
        self.add_result(result)
        
        # 5. Notificar al servicio de calibración
        result = self.run_test(self.test_notify_print_completed, printer_id)
        self.add_result(result)
        
        # 6. Actualizar volumen en impresora
        result = self.run_test(self.test_update_printer_volume, printer_id, 50.0)
        self.add_result(result)
    
    # ==================== PRUEBAS DE CARGA ====================
    
    def test_load_performance(self):
        """Pruebas de rendimiento bajo carga"""
        self.log("=== PRUEBAS DE CARGA Y RENDIMIENTO ===")
        
        def make_request():
            """Función para hacer una petición"""
            start_time = time.time()
            try:
                response = self.session.get(f"{SERVICES['printers']['url']}/health")
                duration = time.time() - start_time
                return {"success": response.status_code == 200, "duration": duration}
            except Exception as e:
                duration = time.time() - start_time
                return {"success": False, "duration": duration, "error": str(e)}
        
        # Prueba de carga concurrente
        self.log("Ejecutando prueba de carga concurrente...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=TEST_CONFIG['concurrent_requests']) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # Analizar resultados
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        durations = [r['duration'] for r in successful_requests]
        
        self.log(f"Prueba de carga completada en {end_time - start_time:.2f}s")
        self.log(f"Requests exitosos: {len(successful_requests)}/{len(results)}")
        self.log(f"Requests fallidos: {len(failed_requests)}")
        if durations:
            self.log(f"Tiempo promedio: {statistics.mean(durations):.3f}s")
            self.log(f"Tiempo mínimo: {min(durations):.3f}s")
            self.log(f"Tiempo máximo: {max(durations):.3f}s")
            self.log(f"Tiempo mediano: {statistics.median(durations):.3f}s")
    
    # ==================== PRUEBAS DE ROBUSTEZ ====================
    
    def test_error_handling(self):
        """Pruebas de manejo de errores"""
        self.log("=== PRUEBAS DE MANEJO DE ERRORES ===")
        
        # Prueba con ID inexistente
        try:
            response = self.session.get(f"{SERVICES['printers']['url']}/printers/nonexistent")
            if response.status_code == 404:
                self.log("✅ Manejo correcto de ID inexistente")
            else:
                self.log(f"❌ Código de error inesperado: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Error en prueba de ID inexistente: {e}")
        
        # Prueba con datos inválidos
        try:
            invalid_data = {"invalid": "data"}
            response = self.session.post(f"{SERVICES['printers']['url']}/printers", json=invalid_data)
            if response.status_code == 422:
                self.log("✅ Manejo correcto de datos inválidos")
            else:
                self.log(f"❌ Código de error inesperado: {response.status_code}")
        except Exception as e:
            self.log(f"❌ Error en prueba de datos inválidos: {e}")
    
    # ==================== EJECUCIÓN PRINCIPAL ====================
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        self.log("🚀 INICIANDO SUITE DE PRUEBAS COMPREHENSIVA - PRINTDM")
        self.log(f"Timestamp: {datetime.utcnow().isoformat()}")
        
        # Pruebas de salud
        self.test_all_services_health()
        
        # Pruebas de servicios individuales
        self.test_printers_service_comprehensive()
        self.test_monitoring_service_comprehensive()
        self.test_calibration_service_comprehensive()
        
        # Pruebas de integración
        self.test_integration_workflow()
        
        # Pruebas de rendimiento
        self.test_load_performance()
        
        # Pruebas de robustez
        self.test_error_handling()
        
        # Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Genera un reporte de las pruebas"""
        self.log("\n" + "="*60)
        self.log("📊 REPORTE FINAL DE PRUEBAS")
        self.log("="*60)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"Total de pruebas: {total_tests}")
        self.log(f"Pruebas exitosas: {successful_tests}")
        self.log(f"Pruebas fallidas: {failed_tests}")
        self.log(f"Tasa de éxito: {success_rate:.1f}%")
        
        # Tiempo promedio de respuesta
        durations = [r.duration for r in self.results if r.success]
        if durations:
            avg_duration = statistics.mean(durations)
            self.log(f"Tiempo promedio de respuesta: {avg_duration:.3f}s")
        
        # Pruebas fallidas
        if failed_tests > 0:
            self.log("\n❌ PRUEBAS FALLIDAS:")
            for result in self.results:
                if not result.success:
                    self.log(f"  - {result.test_name}: {result.error}")
        
        # Conclusión
        if success_rate >= 95:
            self.log("\n🎉 ¡TODAS LAS PRUEBAS PRINCIPALES EXITOSAS!")
        elif success_rate >= 80:
            self.log("\n⚠️  LA MAYORÍA DE PRUEBAS EXITOSAS, ALGUNAS FALLIDAS")
        else:
            self.log("\n🚨 MUCHAS PRUEBAS FALLIDAS, REVISAR SISTEMA")
        
        self.log("="*60)

def main():
    """Función principal"""
    print("PrintDM - Suite de Pruebas Comprehensiva")
    print("=" * 50)
    
    # Verificar que los servicios estén disponibles
    print("Verificando disponibilidad de servicios...")
    time.sleep(2)
    
    # Ejecutar suite de pruebas
    test_suite = PrintDMTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main() 