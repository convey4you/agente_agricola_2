# quick_test_prompt3.py
"""
Teste rápido para validar PROMPT 3 - Monitorização de Performance
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def quick_test():
    print("🚀 TESTE RÁPIDO - SPRINT 4 PROMPT 3")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # 1. Testar imports básicos
    try:
        from app.utils.performance_monitoring import PerformanceMonitor, PerformanceMetric
        print("✅ 1. Imports básicos: OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 1. Imports básicos: {e}")
    
    # 2. Testar criação do monitor
    try:
        monitor = PerformanceMonitor()
        assert monitor.enabled == True
        print("✅ 2. Criação do monitor: OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 2. Criação do monitor: {e}")
    
    # 3. Testar adição de métrica
    try:
        monitor = PerformanceMonitor()
        monitor.add_metric('test', 50.0, '%')
        assert len(monitor.metrics) == 1
        print("✅ 3. Adição de métrica: OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 3. Adição de métrica: {e}")
    
    # 4. Testar controlador
    try:
        from app.controllers.performance_monitoring_controller import performance_monitoring_bp
        assert performance_monitoring_bp.name == 'performance_monitoring'
        print("✅ 4. Controlador: OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 4. Controlador: {e}")
    
    # 5. Testar psutil
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        assert isinstance(cpu, (int, float))
        print("✅ 5. Psutil funcionando: OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ 5. Psutil: {e}")
    
    print(f"\n📊 Resultado: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 PROMPT 3 IMPLEMENTADO COM SUCESSO!")
        print("\n📋 Componentes criados:")
        print("• app/utils/performance_monitoring.py")
        print("• app/controllers/performance_monitoring_controller.py") 
        print("• tests/test_sprint4_performance_monitoring.py")
        print("• Integração com __init__.py")
        print("\n✅ Sistema de monitorização pronto!")
        return True
    else:
        print("⚠️ Alguns componentes precisam ser verificados")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
