# PROMPTS CLAUDE SONNET 4 - FUNCIONALIDADES AVANÇADAS
## AgroTech Portugal - Sistema de Agente Agrícola Inteligente

**Autor**: Manus AI - Gerente de Tecnologia  
**Data**: 31 de julho de 2025  
**Versão**: 1.0  
**Categoria**: Funcionalidades Avançadas e Expansão  
**Período**: Outubro 2025 - Março 2026  

---

## 📋 VISÃO GERAL DAS FUNCIONALIDADES AVANÇADAS

As funcionalidades avançadas representam a evolução natural do AgroTech Portugal após o lançamento bem-sucedido. Estas funcionalidades posicionam a plataforma como líder em inovação agrícola, oferecendo capacidades que vão além das necessidades básicas dos agricultores, criando valor diferenciado e vantagem competitiva sustentável no mercado português e europeu.

### Objetivos Estratégicos

O desenvolvimento de funcionalidades avançadas tem como objetivo consolidar o AgroTech Portugal como a plataforma de referência em tecnologia agrícola na Europa, expandindo as capacidades da plataforma para incluir Internet das Coisas (IoT), inteligência artificial avançada, análise preditiva, automação inteligente e integração com sistemas empresariais. Estas funcionalidades criarão um ecossistema completo que suporte desde pequenos agricultores familiares até grandes operações agrícolas comerciais.

### Contexto de Inovação

A agricultura moderna está passando por uma transformação digital acelerada, impulsionada pela necessidade de maior eficiência, sustentabilidade e produtividade. As funcionalidades avançadas do AgroTech Portugal aproveitam tecnologias emergentes como sensores IoT, machine learning avançado, análise de big data e automação para criar soluções que antecipam problemas, otimizam recursos e maximizam resultados para os agricultores portugueses.

---

## 🌐 PROMPT 1: SISTEMA IoT E SENSORES INTELIGENTES

### Contexto do Projeto
Você está implementando um sistema abrangente de Internet das Coisas (IoT) para o AgroTech Portugal. Este sistema deve integrar sensores inteligentes, dispositivos de monitoramento, estações meteorológicas locais, sistemas de irrigação automatizada e outros equipamentos agrícolas conectados para criar um ecossistema de agricultura de precisão que forneça dados em tempo real e automação inteligente.

### Funcionalidade a Implementar
Sistema completo de IoT que inclui integração com sensores de solo, estações meteorológicas, câmeras de monitoramento, sistemas de irrigação, drones agrícolas, tratores conectados e outros dispositivos inteligentes. O sistema deve coletar, processar e analisar dados em tempo real, fornecendo insights acionáveis e automação baseada em regras definidas pelo usuário.

### Arquitetura Proposta

O sistema IoT será baseado em uma arquitetura distribuída que suporte múltiplos protocolos de comunicação, processamento edge computing, armazenamento de séries temporais e integração com sistemas de automação. A arquitetura utilizará MQTT para comunicação, InfluxDB para dados de sensores, Redis para cache de tempo real e Python para processamento de dados.

**Componentes do Sistema IoT:**
- **Device Management**: Gestão centralizada de dispositivos IoT
- **Data Ingestion**: Coleta de dados de múltiplas fontes
- **Real-time Processing**: Processamento de dados em tempo real
- **Automation Engine**: Motor de automação baseado em regras
- **Edge Computing**: Processamento local para baixa latência
- **Device Integration**: APIs para integração com equipamentos

### Objetivo
Implementar um sistema robusto de IoT que transforme propriedades agrícolas portuguesas em operações de agricultura de precisão, fornecendo monitoramento contínuo, automação inteligente e otimização de recursos baseada em dados em tempo real.

### Instruções Detalhadas

**ETAPA 1: Sistema de Gestão de Dispositivos IoT**

Crie o sistema de gestão em `app/iot/device_manager.py`:

```python
# app/iot/device_manager.py
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio
import paho.mqtt.client as mqtt
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.models import db

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """Tipos de dispositivos IoT suportados"""
    SOIL_SENSOR = "soil_sensor"
    WEATHER_STATION = "weather_station"
    IRRIGATION_CONTROLLER = "irrigation_controller"
    CAMERA = "camera"
    DRONE = "drone"
    TRACTOR = "tractor"
    GREENHOUSE_CONTROLLER = "greenhouse_controller"
    LIVESTOCK_TRACKER = "livestock_tracker"

class DeviceStatus(Enum):
    """Status do dispositivo"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class SensorReading:
    """Leitura de sensor"""
    device_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    location: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

class IoTDevice(db.Model):
    """Modelo de dispositivo IoT"""
    __tablename__ = 'iot_devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    firmware_version = Column(String(50))
    
    # Localização
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    
    # Status
    status = Column(String(20), default='offline')
    last_seen = Column(DateTime)
    battery_level = Column(Float)
    signal_strength = Column(Float)
    
    # Configuração
    configuration = Column(Text)  # JSON
    calibration_data = Column(Text)  # JSON
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    culture_id = Column(Integer, ForeignKey('cultures.id'))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", backref="iot_devices")
    culture = relationship("Culture", backref="iot_devices")
    readings = relationship("SensorReading", backref="device", cascade="all, delete-orphan")

class SensorReadingModel(db.Model):
    """Modelo de leitura de sensor"""
    __tablename__ = 'sensor_readings'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), ForeignKey('iot_devices.device_id'), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Localização (pode ser diferente do dispositivo para sensores móveis)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Metadados adicionais
    metadata = Column(Text)  # JSON
    
    # Qualidade do dado
    quality_score = Column(Float, default=1.0)
    is_anomaly = Column(Boolean, default=False)

class DeviceManager:
    """Gerenciador de dispositivos IoT"""
    
    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = None
        self.devices: Dict[str, IoTDevice] = {}
        self.device_handlers: Dict[DeviceType, Any] = {}
        self.running = False
        
        self._setup_device_handlers()
    
    def _setup_device_handlers(self):
        """Configurar handlers para diferentes tipos de dispositivos"""
        self.device_handlers = {
            DeviceType.SOIL_SENSOR: SoilSensorHandler(),
            DeviceType.WEATHER_STATION: WeatherStationHandler(),
            DeviceType.IRRIGATION_CONTROLLER: IrrigationControllerHandler(),
            DeviceType.CAMERA: CameraHandler(),
            DeviceType.DRONE: DroneHandler(),
            DeviceType.TRACTOR: TractorHandler(),
            DeviceType.GREENHOUSE_CONTROLLER: GreenhouseControllerHandler(),
            DeviceType.LIVESTOCK_TRACKER: LivestockTrackerHandler()
        }
    
    async def start(self):
        """Iniciar gerenciador de dispositivos"""
        self.running = True
        
        # Conectar ao MQTT
        await self._connect_mqtt()
        
        # Carregar dispositivos do banco de dados
        await self._load_devices()
        
        # Iniciar loop de monitoramento
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("Device Manager started successfully")
    
    async def stop(self):
        """Parar gerenciador de dispositivos"""
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        logger.info("Device Manager stopped")
    
    async def _connect_mqtt(self):
        """Conectar ao broker MQTT"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        
        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Callback de conexão MQTT"""
        if rc == 0:
            logger.info("MQTT connection successful")
            # Subscrever tópicos
            client.subscribe("agrotech/devices/+/data")
            client.subscribe("agrotech/devices/+/status")
            client.subscribe("agrotech/devices/+/heartbeat")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Callback de mensagem MQTT"""
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 4:
                device_id = topic_parts[2]
                message_type = topic_parts[3]
                
                payload = json.loads(msg.payload.decode())
                
                asyncio.create_task(self._handle_mqtt_message(device_id, message_type, payload))
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Callback de desconexão MQTT"""
        logger.warning(f"MQTT disconnected with code {rc}")
    
    async def _handle_mqtt_message(self, device_id: str, message_type: str, payload: Dict):
        """Processar mensagem MQTT"""
        try:
            if message_type == "data":
                await self._process_sensor_data(device_id, payload)
            elif message_type == "status":
                await self._process_device_status(device_id, payload)
            elif message_type == "heartbeat":
                await self._process_heartbeat(device_id, payload)
            
        except Exception as e:
            logger.error(f"Error handling MQTT message for device {device_id}: {e}")
    
    async def _process_sensor_data(self, device_id: str, data: Dict):
        """Processar dados de sensor"""
        device = await self._get_device(device_id)
        if not device:
            logger.warning(f"Received data from unknown device: {device_id}")
            return
        
        # Obter handler do dispositivo
        device_type = DeviceType(device.device_type)
        handler = self.device_handlers.get(device_type)
        
        if handler:
            readings = await handler.process_data(device, data)
            
            # Salvar leituras no banco de dados
            for reading in readings:
                await self._save_sensor_reading(reading)
            
            # Executar automações baseadas nos dados
            await self._trigger_automations(device, readings)
        
        # Atualizar último contato
        device.last_seen = datetime.utcnow()
        device.status = DeviceStatus.ONLINE.value
        db.session.commit()
    
    async def _process_device_status(self, device_id: str, status_data: Dict):
        """Processar status do dispositivo"""
        device = await self._get_device(device_id)
        if not device:
            return
        
        # Atualizar status
        device.status = status_data.get('status', 'online')
        device.battery_level = status_data.get('battery_level')
        device.signal_strength = status_data.get('signal_strength')
        device.last_seen = datetime.utcnow()
        
        # Verificar se precisa de manutenção
        if device.battery_level and device.battery_level < 20:
            await self._create_maintenance_alert(device, "Bateria baixa")
        
        db.session.commit()
    
    async def _process_heartbeat(self, device_id: str, heartbeat_data: Dict):
        """Processar heartbeat do dispositivo"""
        device = await self._get_device(device_id)
        if not device:
            return
        
        device.last_seen = datetime.utcnow()
        if device.status == DeviceStatus.OFFLINE.value:
            device.status = DeviceStatus.ONLINE.value
            logger.info(f"Device {device_id} is back online")
        
        db.session.commit()
    
    async def _get_device(self, device_id: str) -> Optional[IoTDevice]:
        """Obter dispositivo por ID"""
        if device_id in self.devices:
            return self.devices[device_id]
        
        # Buscar no banco de dados
        device = IoTDevice.query.filter_by(device_id=device_id).first()
        if device:
            self.devices[device_id] = device
        
        return device
    
    async def _save_sensor_reading(self, reading: SensorReading):
        """Salvar leitura de sensor no banco de dados"""
        db_reading = SensorReadingModel(
            device_id=reading.device_id,
            sensor_type=reading.sensor_type,
            value=reading.value,
            unit=reading.unit,
            timestamp=reading.timestamp,
            latitude=reading.location.get('lat') if reading.location else None,
            longitude=reading.location.get('lng') if reading.location else None,
            metadata=json.dumps(reading.metadata) if reading.metadata else None
        )
        
        db.session.add(db_reading)
        db.session.commit()
    
    async def _trigger_automations(self, device: IoTDevice, readings: List[SensorReading]):
        """Executar automações baseadas nas leituras"""
        # Implementar lógica de automação
        # Por exemplo, irrigação automática baseada em umidade do solo
        
        for reading in readings:
            if reading.sensor_type == "soil_moisture" and reading.value < 30:
                # Ativar irrigação se umidade do solo estiver baixa
                await self._trigger_irrigation(device.culture_id, "low_moisture")
            
            elif reading.sensor_type == "temperature" and reading.value > 35:
                # Alerta de temperatura alta
                await self._create_temperature_alert(device, reading.value)
    
    async def _trigger_irrigation(self, culture_id: int, reason: str):
        """Ativar sistema de irrigação"""
        # Buscar controladores de irrigação para a cultura
        irrigation_devices = IoTDevice.query.filter_by(
            culture_id=culture_id,
            device_type=DeviceType.IRRIGATION_CONTROLLER.value,
            status=DeviceStatus.ONLINE.value
        ).all()
        
        for device in irrigation_devices:
            command = {
                "action": "start_irrigation",
                "duration": 30,  # minutos
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self._send_device_command(device.device_id, command)
    
    async def _send_device_command(self, device_id: str, command: Dict):
        """Enviar comando para dispositivo"""
        if self.mqtt_client:
            topic = f"agrotech/devices/{device_id}/commands"
            payload = json.dumps(command)
            
            self.mqtt_client.publish(topic, payload)
            logger.info(f"Command sent to device {device_id}: {command['action']}")
    
    async def _monitoring_loop(self):
        """Loop de monitoramento de dispositivos"""
        while self.running:
            try:
                # Verificar dispositivos offline
                offline_threshold = datetime.utcnow() - timedelta(minutes=10)
                
                for device in self.devices.values():
                    if (device.last_seen and 
                        device.last_seen < offline_threshold and 
                        device.status != DeviceStatus.OFFLINE.value):
                        
                        device.status = DeviceStatus.OFFLINE.value
                        db.session.commit()
                        
                        logger.warning(f"Device {device.device_id} marked as offline")
                        await self._create_offline_alert(device)
                
                await asyncio.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _load_devices(self):
        """Carregar dispositivos do banco de dados"""
        devices = IoTDevice.query.all()
        for device in devices:
            self.devices[device.device_id] = device
        
        logger.info(f"Loaded {len(devices)} devices from database")
    
    async def register_device(self, device_data: Dict) -> IoTDevice:
        """Registrar novo dispositivo"""
        device = IoTDevice(
            device_id=device_data['device_id'],
            name=device_data['name'],
            device_type=device_data['device_type'],
            manufacturer=device_data.get('manufacturer'),
            model=device_data.get('model'),
            firmware_version=device_data.get('firmware_version'),
            latitude=device_data.get('latitude'),
            longitude=device_data.get('longitude'),
            altitude=device_data.get('altitude'),
            user_id=device_data['user_id'],
            culture_id=device_data.get('culture_id'),
            configuration=json.dumps(device_data.get('configuration', {}))
        )
        
        db.session.add(device)
        db.session.commit()
        
        self.devices[device.device_id] = device
        
        logger.info(f"Device registered: {device.device_id}")
        return device
    
    async def _create_maintenance_alert(self, device: IoTDevice, message: str):
        """Criar alerta de manutenção"""
        # Implementar criação de alerta
        pass
    
    async def _create_temperature_alert(self, device: IoTDevice, temperature: float):
        """Criar alerta de temperatura"""
        # Implementar criação de alerta
        pass
    
    async def _create_offline_alert(self, device: IoTDevice):
        """Criar alerta de dispositivo offline"""
        # Implementar criação de alerta
        pass

# Handlers para diferentes tipos de dispositivos
class DeviceHandler:
    """Classe base para handlers de dispositivos"""
    
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        """Processar dados do dispositivo"""
        raise NotImplementedError

class SoilSensorHandler(DeviceHandler):
    """Handler para sensores de solo"""
    
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        readings = []
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
        
        # Processar diferentes tipos de sensores de solo
        if 'moisture' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="soil_moisture",
                value=data['moisture'],
                unit="%",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        if 'temperature' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="soil_temperature",
                value=data['temperature'],
                unit="°C",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        if 'ph' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="soil_ph",
                value=data['ph'],
                unit="pH",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        if 'conductivity' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="soil_conductivity",
                value=data['conductivity'],
                unit="µS/cm",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        return readings

class WeatherStationHandler(DeviceHandler):
    """Handler para estações meteorológicas"""
    
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        readings = []
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
        
        # Mapear dados meteorológicos
        sensor_mappings = {
            'temperature': ('air_temperature', '°C'),
            'humidity': ('air_humidity', '%'),
            'pressure': ('atmospheric_pressure', 'hPa'),
            'wind_speed': ('wind_speed', 'm/s'),
            'wind_direction': ('wind_direction', '°'),
            'rainfall': ('rainfall', 'mm'),
            'solar_radiation': ('solar_radiation', 'W/m²'),
            'uv_index': ('uv_index', 'UV')
        }
        
        for data_key, (sensor_type, unit) in sensor_mappings.items():
            if data_key in data:
                readings.append(SensorReading(
                    device_id=device.device_id,
                    sensor_type=sensor_type,
                    value=data[data_key],
                    unit=unit,
                    timestamp=timestamp,
                    location={'lat': device.latitude, 'lng': device.longitude}
                ))
        
        return readings

class IrrigationControllerHandler(DeviceHandler):
    """Handler para controladores de irrigação"""
    
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        readings = []
        timestamp = datetime.fromisoformat(data.get('timestamp', datetime.utcnow().isoformat()))
        
        # Dados de irrigação
        if 'flow_rate' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="irrigation_flow_rate",
                value=data['flow_rate'],
                unit="L/min",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        if 'pressure' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="irrigation_pressure",
                value=data['pressure'],
                unit="bar",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        if 'valve_status' in data:
            readings.append(SensorReading(
                device_id=device.device_id,
                sensor_type="valve_status",
                value=1 if data['valve_status'] == 'open' else 0,
                unit="boolean",
                timestamp=timestamp,
                location={'lat': device.latitude, 'lng': device.longitude}
            ))
        
        return readings

# Implementar outros handlers...
class CameraHandler(DeviceHandler):
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        # Implementar processamento de dados de câmera
        return []

class DroneHandler(DeviceHandler):
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        # Implementar processamento de dados de drone
        return []

class TractorHandler(DeviceHandler):
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        # Implementar processamento de dados de trator
        return []

class GreenhouseControllerHandler(DeviceHandler):
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        # Implementar processamento de dados de estufa
        return []

class LivestockTrackerHandler(DeviceHandler):
    async def process_data(self, device: IoTDevice, data: Dict) -> List[SensorReading]:
        # Implementar processamento de dados de gado
        return []

# Instância global do gerenciador
device_manager = DeviceManager()
```

**ETAPA 2: API REST para Integração IoT**

Crie API para dispositivos em `app/api/iot_api.py`:

```python
# app/api/iot_api.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
from app.iot.device_manager import device_manager, IoTDevice, SensorReadingModel, DeviceType
from app.models import db
from app.utils.validators import validate_json
from app.utils.permissions import require_permission

iot_bp = Blueprint('iot', __name__, url_prefix='/api/iot')

@iot_bp.route('/devices', methods=['GET'])
@login_required
def get_devices():
    """Obter dispositivos do usuário"""
    try:
        devices = IoTDevice.query.filter_by(user_id=current_user.id).all()
        
        devices_data = []
        for device in devices:
            device_data = {
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name,
                'device_type': device.device_type,
                'manufacturer': device.manufacturer,
                'model': device.model,
                'status': device.status,
                'last_seen': device.last_seen.isoformat() if device.last_seen else None,
                'battery_level': device.battery_level,
                'signal_strength': device.signal_strength,
                'location': {
                    'latitude': device.latitude,
                    'longitude': device.longitude,
                    'altitude': device.altitude
                } if device.latitude and device.longitude else None,
                'culture_id': device.culture_id,
                'created_at': device.created_at.isoformat()
            }
            devices_data.append(device_data)
        
        return jsonify({
            'success': True,
            'devices': devices_data,
            'total': len(devices_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting devices: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/devices', methods=['POST'])
@login_required
@validate_json(['device_id', 'name', 'device_type'])
def register_device():
    """Registrar novo dispositivo"""
    try:
        data = request.get_json()
        
        # Verificar se device_id já existe
        existing_device = IoTDevice.query.filter_by(device_id=data['device_id']).first()
        if existing_device:
            return jsonify({
                'success': False,
                'error': 'Dispositivo já registrado'
            }), 400
        
        # Validar tipo de dispositivo
        try:
            DeviceType(data['device_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Tipo de dispositivo inválido'
            }), 400
        
        # Preparar dados do dispositivo
        device_data = {
            'device_id': data['device_id'],
            'name': data['name'],
            'device_type': data['device_type'],
            'manufacturer': data.get('manufacturer'),
            'model': data.get('model'),
            'firmware_version': data.get('firmware_version'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'altitude': data.get('altitude'),
            'user_id': current_user.id,
            'culture_id': data.get('culture_id'),
            'configuration': data.get('configuration', {})
        }
        
        # Registrar dispositivo
        device = await device_manager.register_device(device_data)
        
        return jsonify({
            'success': True,
            'message': 'Dispositivo registrado com sucesso',
            'device': {
                'id': device.id,
                'device_id': device.device_id,
                'name': device.name,
                'device_type': device.device_type,
                'status': device.status
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error registering device: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/devices/<device_id>', methods=['GET'])
@login_required
def get_device(device_id):
    """Obter detalhes de um dispositivo"""
    try:
        device = IoTDevice.query.filter_by(
            device_id=device_id,
            user_id=current_user.id
        ).first()
        
        if not device:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        # Obter últimas leituras
        recent_readings = SensorReadingModel.query.filter_by(
            device_id=device_id
        ).order_by(SensorReadingModel.timestamp.desc()).limit(10).all()
        
        readings_data = []
        for reading in recent_readings:
            readings_data.append({
                'sensor_type': reading.sensor_type,
                'value': reading.value,
                'unit': reading.unit,
                'timestamp': reading.timestamp.isoformat(),
                'quality_score': reading.quality_score,
                'is_anomaly': reading.is_anomaly
            })
        
        device_data = {
            'id': device.id,
            'device_id': device.device_id,
            'name': device.name,
            'device_type': device.device_type,
            'manufacturer': device.manufacturer,
            'model': device.model,
            'firmware_version': device.firmware_version,
            'status': device.status,
            'last_seen': device.last_seen.isoformat() if device.last_seen else None,
            'battery_level': device.battery_level,
            'signal_strength': device.signal_strength,
            'location': {
                'latitude': device.latitude,
                'longitude': device.longitude,
                'altitude': device.altitude
            } if device.latitude and device.longitude else None,
            'culture_id': device.culture_id,
            'configuration': json.loads(device.configuration) if device.configuration else {},
            'recent_readings': readings_data,
            'created_at': device.created_at.isoformat(),
            'updated_at': device.updated_at.isoformat()
        }
        
        return jsonify({
            'success': True,
            'device': device_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting device {device_id}: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/devices/<device_id>/readings', methods=['GET'])
@login_required
def get_device_readings(device_id):
    """Obter leituras de um dispositivo"""
    try:
        # Verificar se dispositivo pertence ao usuário
        device = IoTDevice.query.filter_by(
            device_id=device_id,
            user_id=current_user.id
        ).first()
        
        if not device:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        # Parâmetros de consulta
        sensor_type = request.args.get('sensor_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        # Construir query
        query = SensorReadingModel.query.filter_by(device_id=device_id)
        
        if sensor_type:
            query = query.filter_by(sensor_type=sensor_type)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(SensorReadingModel.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(SensorReadingModel.timestamp <= end_dt)
        
        readings = query.order_by(
            SensorReadingModel.timestamp.desc()
        ).limit(limit).all()
        
        readings_data = []
        for reading in readings:
            readings_data.append({
                'id': reading.id,
                'sensor_type': reading.sensor_type,
                'value': reading.value,
                'unit': reading.unit,
                'timestamp': reading.timestamp.isoformat(),
                'location': {
                    'latitude': reading.latitude,
                    'longitude': reading.longitude
                } if reading.latitude and reading.longitude else None,
                'metadata': json.loads(reading.metadata) if reading.metadata else {},
                'quality_score': reading.quality_score,
                'is_anomaly': reading.is_anomaly
            })
        
        return jsonify({
            'success': True,
            'readings': readings_data,
            'total': len(readings_data),
            'device_id': device_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting readings for device {device_id}: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/devices/<device_id>/command', methods=['POST'])
@login_required
@validate_json(['action'])
def send_device_command(device_id):
    """Enviar comando para dispositivo"""
    try:
        # Verificar se dispositivo pertence ao usuário
        device = IoTDevice.query.filter_by(
            device_id=device_id,
            user_id=current_user.id
        ).first()
        
        if not device:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        if device.status != 'online':
            return jsonify({
                'success': False,
                'error': 'Dispositivo não está online'
            }), 400
        
        data = request.get_json()
        
        # Preparar comando
        command = {
            'action': data['action'],
            'parameters': data.get('parameters', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': current_user.id
        }
        
        # Enviar comando
        await device_manager._send_device_command(device_id, command)
        
        return jsonify({
            'success': True,
            'message': 'Comando enviado com sucesso',
            'command': command
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending command to device {device_id}: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/devices/<device_id>/configuration', methods=['PUT'])
@login_required
def update_device_configuration(device_id):
    """Atualizar configuração do dispositivo"""
    try:
        # Verificar se dispositivo pertence ao usuário
        device = IoTDevice.query.filter_by(
            device_id=device_id,
            user_id=current_user.id
        ).first()
        
        if not device:
            return jsonify({'success': False, 'error': 'Dispositivo não encontrado'}), 404
        
        data = request.get_json()
        configuration = data.get('configuration', {})
        
        # Atualizar configuração
        device.configuration = json.dumps(configuration)
        device.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Enviar nova configuração para o dispositivo
        if device.status == 'online':
            config_command = {
                'action': 'update_configuration',
                'parameters': configuration,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await device_manager._send_device_command(device_id, config_command)
        
        return jsonify({
            'success': True,
            'message': 'Configuração atualizada com sucesso'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating device configuration {device_id}: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/analytics/summary', methods=['GET'])
@login_required
def get_iot_analytics_summary():
    """Obter resumo de analytics IoT"""
    try:
        user_devices = IoTDevice.query.filter_by(user_id=current_user.id).all()
        device_ids = [d.device_id for d in user_devices]
        
        if not device_ids:
            return jsonify({
                'success': True,
                'summary': {
                    'total_devices': 0,
                    'online_devices': 0,
                    'offline_devices': 0,
                    'recent_readings': 0,
                    'device_types': {}
                }
            })
        
        # Estatísticas básicas
        total_devices = len(user_devices)
        online_devices = len([d for d in user_devices if d.status == 'online'])
        offline_devices = total_devices - online_devices
        
        # Leituras recentes (últimas 24 horas)
        recent_readings = SensorReadingModel.query.filter(
            SensorReadingModel.device_id.in_(device_ids),
            SensorReadingModel.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Tipos de dispositivos
        device_types = {}
        for device in user_devices:
            device_type = device.device_type
            if device_type not in device_types:
                device_types[device_type] = 0
            device_types[device_type] += 1
        
        summary = {
            'total_devices': total_devices,
            'online_devices': online_devices,
            'offline_devices': offline_devices,
            'recent_readings': recent_readings,
            'device_types': device_types
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting IoT analytics summary: {e}")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@iot_bp.route('/device-types', methods=['GET'])
@login_required
def get_device_types():
    """Obter tipos de dispositivos suportados"""
    device_types = []
    
    for device_type in DeviceType:
        device_types.append({
            'value': device_type.value,
            'name': device_type.value.replace('_', ' ').title(),
            'description': get_device_type_description(device_type)
        })
    
    return jsonify({
        'success': True,
        'device_types': device_types
    })

def get_device_type_description(device_type: DeviceType) -> str:
    """Obter descrição do tipo de dispositivo"""
    descriptions = {
        DeviceType.SOIL_SENSOR: "Sensores para monitoramento de solo (umidade, pH, temperatura)",
        DeviceType.WEATHER_STATION: "Estação meteorológica para dados climáticos locais",
        DeviceType.IRRIGATION_CONTROLLER: "Controlador de sistema de irrigação automatizada",
        DeviceType.CAMERA: "Câmera para monitoramento visual das culturas",
        DeviceType.DRONE: "Drone para monitoramento aéreo e pulverização",
        DeviceType.TRACTOR: "Trator conectado com telemetria e GPS",
        DeviceType.GREENHOUSE_CONTROLLER: "Controlador de ambiente de estufa",
        DeviceType.LIVESTOCK_TRACKER: "Rastreador para monitoramento de gado"
    }
    
    return descriptions.get(device_type, "Dispositivo IoT genérico")
```

### Testes de Validação

**TESTE 1: Validação do Device Manager**
```python
# Testar registro de dispositivo
device_data = {
    'device_id': 'test_sensor_001',
    'name': 'Sensor de Solo - Campo 1',
    'device_type': 'soil_sensor',
    'user_id': 1,
    'latitude': 41.1579,
    'longitude': -8.6291
}

device = await device_manager.register_device(device_data)
assert device.device_id == 'test_sensor_001'
```

**TESTE 2: Validação da API IoT**
```python
# Testar endpoint de dispositivos
with app.test_client() as client:
    response = client.get('/api/iot/devices', headers={'Authorization': 'Bearer token'})
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] == True
```

**TESTE 3: Validação do MQTT**
```python
# Testar comunicação MQTT
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

# Simular dados de sensor
test_data = {
    'moisture': 45.2,
    'temperature': 22.5,
    'timestamp': datetime.utcnow().isoformat()
}

client.publish("agrotech/devices/test_sensor_001/data", json.dumps(test_data))
```

### Critérios de Aceitação
- Sistema de gestão de dispositivos IoT funcionando
- Comunicação MQTT estabelecida e estável
- API REST para integração com dispositivos
- Handlers para diferentes tipos de dispositivos
- Armazenamento de dados de sensores
- Sistema de automação baseado em regras

### Entregáveis Esperados
1. **Sistema de Gestão de Dispositivos** completo
2. **Comunicação MQTT** robusta e escalável
3. **API REST** para integração de dispositivos
4. **Handlers** para tipos específicos de dispositivos
5. **Sistema de Automação** baseado em dados IoT

### Informações Importantes
- Implementar segurança robusta para comunicação MQTT
- Garantir escalabilidade para milhares de dispositivos
- Estabelecer protocolos de failover e recuperação
- Implementar compressão de dados para eficiência
- Configurar alertas para dispositivos offline

---


## 🧠 PROMPT 2: SISTEMA DE IA AVANÇADA E MACHINE LEARNING

### Contexto do Projeto
Você está implementando um sistema avançado de inteligência artificial e machine learning para o AgroTech Portugal. Este sistema deve utilizar algoritmos de aprendizado de máquina, redes neurais, análise preditiva e processamento de linguagem natural para fornecer insights inteligentes, previsões precisas, recomendações personalizadas e automação cognitiva que revolucionem a agricultura portuguesa.

### Funcionalidade a Implementar
Sistema completo de IA que inclui modelos de previsão de safra, detecção de doenças em plantas, otimização de irrigação, análise de imagens por satélite, processamento de linguagem natural para consultas, sistema de recomendações adaptativo, análise preditiva de mercado e automação inteligente baseada em padrões históricos e dados em tempo real.

### Arquitetura Proposta

O sistema de IA será baseado em uma arquitetura de microserviços que suporte múltiplos modelos de machine learning, processamento distribuído, treinamento contínuo e inferência em tempo real. A arquitetura utilizará TensorFlow/PyTorch para modelos, MLflow para gestão de modelos, Apache Kafka para streaming de dados e Redis para cache de predições.

**Componentes do Sistema de IA:**
- **Model Management**: Gestão de modelos de ML e versionamento
- **Training Pipeline**: Pipeline de treinamento automatizado
- **Inference Engine**: Motor de inferência em tempo real
- **Feature Store**: Armazenamento de features para ML
- **Model Monitoring**: Monitoramento de performance dos modelos
- **AutoML**: Otimização automática de hiperparâmetros

### Objetivo
Implementar um sistema robusto de IA que transforme dados agrícolas em insights acionáveis, fornecendo previsões precisas, recomendações personalizadas e automação inteligente que maximize a produtividade e sustentabilidade das operações agrícolas portuguesas.

### Instruções Detalhadas

**ETAPA 1: Sistema de Gestão de Modelos ML**

Crie o sistema de ML em `app/ml/model_manager.py`:

```python
# app/ml/model_manager.py
import os
import json
import pickle
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import asyncio
from pathlib import Path

# ML Libraries
import tensorflow as tf
import torch
import sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

# Computer Vision
import cv2
from PIL import Image
import torchvision.transforms as transforms

# NLP
from transformers import pipeline, AutoTokenizer, AutoModel
import spacy

# MLOps
import mlflow
import mlflow.sklearn
import mlflow.tensorflow
import mlflow.pytorch

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, LargeBinary
from app.models import db

logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Métricas de performance do modelo"""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    r2_score: Optional[float] = None

@dataclass
class PredictionResult:
    """Resultado de predição"""
    prediction: Any
    confidence: float
    model_version: str
    timestamp: datetime
    features_used: List[str]
    metadata: Dict[str, Any]

class MLModel(db.Model):
    """Modelo de ML no banco de dados"""
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    version = Column(String(50), nullable=False)
    model_type = Column(String(100), nullable=False)  # crop_prediction, disease_detection, etc.
    algorithm = Column(String(100), nullable=False)  # random_forest, neural_network, etc.
    
    # Metadados do modelo
    description = Column(Text)
    features = Column(Text)  # JSON list of feature names
    target_variable = Column(String(100))
    
    # Performance
    metrics = Column(Text)  # JSON metrics
    training_accuracy = Column(Float)
    validation_accuracy = Column(Float)
    test_accuracy = Column(Float)
    
    # Arquivos
    model_path = Column(String(500))  # Path to serialized model
    scaler_path = Column(String(500))  # Path to feature scaler
    encoder_path = Column(String(500))  # Path to label encoder
    
    # Status
    is_active = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)
    
    # Timestamps
    trained_at = Column(DateTime, nullable=False)
    deployed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModelManager:
    """Gerenciador de modelos de Machine Learning"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.loaded_models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.encoders: Dict[str, Any] = {}
        
        # Configurar MLflow
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        
        # Carregar modelos ativos
        asyncio.create_task(self._load_active_models())
    
    async def _load_active_models(self):
        """Carregar modelos ativos na memória"""
        try:
            active_models = MLModel.query.filter_by(is_active=True).all()
            
            for model_record in active_models:
                await self._load_model(model_record)
            
            logger.info(f"Loaded {len(active_models)} active models")
            
        except Exception as e:
            logger.error(f"Error loading active models: {e}")
    
    async def _load_model(self, model_record: MLModel):
        """Carregar modelo específico na memória"""
        try:
            model_key = f"{model_record.name}_{model_record.version}"
            
            # Carregar modelo
            if model_record.model_path and os.path.exists(model_record.model_path):
                if model_record.algorithm.startswith('tensorflow'):
                    model = tf.keras.models.load_model(model_record.model_path)
                elif model_record.algorithm.startswith('pytorch'):
                    model = torch.load(model_record.model_path)
                else:
                    model = joblib.load(model_record.model_path)
                
                self.loaded_models[model_key] = model
            
            # Carregar scaler
            if model_record.scaler_path and os.path.exists(model_record.scaler_path):
                scaler = joblib.load(model_record.scaler_path)
                self.scalers[model_key] = scaler
            
            # Carregar encoder
            if model_record.encoder_path and os.path.exists(model_record.encoder_path):
                encoder = joblib.load(model_record.encoder_path)
                self.encoders[model_key] = encoder
            
            logger.info(f"Model loaded: {model_key}")
            
        except Exception as e:
            logger.error(f"Error loading model {model_record.name}: {e}")
    
    async def train_crop_yield_model(self, culture_data: pd.DataFrame) -> MLModel:
        """Treinar modelo de previsão de safra"""
        try:
            with mlflow.start_run(run_name="crop_yield_prediction"):
                # Preparar dados
                features = [
                    'area', 'soil_ph', 'soil_moisture', 'temperature_avg',
                    'rainfall_total', 'fertilizer_amount', 'days_planted'
                ]
                
                X = culture_data[features]
                y = culture_data['yield_kg_per_hectare']
                
                # Dividir dados
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Normalizar features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Treinar modelo
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                
                model.fit(X_train_scaled, y_train)
                
                # Avaliar modelo
                train_pred = model.predict(X_train_scaled)
                test_pred = model.predict(X_test_scaled)
                
                train_mse = mean_squared_error(y_train, train_pred)
                test_mse = mean_squared_error(y_test, test_pred)
                train_r2 = model.score(X_train_scaled, y_train)
                test_r2 = model.score(X_test_scaled, y_test)
                
                # Log métricas no MLflow
                mlflow.log_param("n_estimators", 100)
                mlflow.log_param("max_depth", 10)
                mlflow.log_metric("train_mse", train_mse)
                mlflow.log_metric("test_mse", test_mse)
                mlflow.log_metric("train_r2", train_r2)
                mlflow.log_metric("test_r2", test_r2)
                
                # Salvar modelo
                model_name = "crop_yield_prediction"
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                model_path = self.models_dir / f"{model_name}_{version}.joblib"
                scaler_path = self.models_dir / f"{model_name}_{version}_scaler.joblib"
                
                joblib.dump(model, model_path)
                joblib.dump(scaler, scaler_path)
                
                # Log modelo no MLflow
                mlflow.sklearn.log_model(model, "model")
                
                # Salvar no banco de dados
                metrics = ModelMetrics(
                    mse=test_mse,
                    rmse=np.sqrt(test_mse),
                    r2_score=test_r2
                )
                
                model_record = MLModel(
                    name=model_name,
                    version=version,
                    model_type="regression",
                    algorithm="random_forest",
                    description="Modelo de previsão de produtividade de culturas",
                    features=json.dumps(features),
                    target_variable="yield_kg_per_hectare",
                    metrics=json.dumps(metrics.__dict__),
                    training_accuracy=train_r2,
                    validation_accuracy=test_r2,
                    model_path=str(model_path),
                    scaler_path=str(scaler_path),
                    trained_at=datetime.utcnow()
                )
                
                db.session.add(model_record)
                db.session.commit()
                
                logger.info(f"Crop yield model trained successfully: {version}")
                return model_record
                
        except Exception as e:
            logger.error(f"Error training crop yield model: {e}")
            raise
    
    async def train_disease_detection_model(self, image_data: List[Tuple[str, str]]) -> MLModel:
        """Treinar modelo de detecção de doenças"""
        try:
            with mlflow.start_run(run_name="disease_detection"):
                # Preparar dados de imagem
                images = []
                labels = []
                
                for image_path, disease_label in image_data:
                    img = cv2.imread(image_path)
                    img = cv2.resize(img, (224, 224))
                    img = img / 255.0  # Normalizar
                    
                    images.append(img)
                    labels.append(disease_label)
                
                X = np.array(images)
                y = np.array(labels)
                
                # Encoder para labels
                label_encoder = LabelEncoder()
                y_encoded = label_encoder.fit_transform(y)
                
                # Dividir dados
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_encoded, test_size=0.2, random_state=42
                )
                
                # Criar modelo CNN com TensorFlow
                model = tf.keras.Sequential([
                    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
                    tf.keras.layers.MaxPooling2D(2, 2),
                    tf.keras.layers.Flatten(),
                    tf.keras.layers.Dense(512, activation='relu'),
                    tf.keras.layers.Dropout(0.5),
                    tf.keras.layers.Dense(len(label_encoder.classes_), activation='softmax')
                ])
                
                model.compile(
                    optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                # Treinar modelo
                history = model.fit(
                    X_train, y_train,
                    epochs=50,
                    batch_size=32,
                    validation_data=(X_test, y_test),
                    verbose=1
                )
                
                # Avaliar modelo
                train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
                test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
                
                # Log métricas
                mlflow.log_param("epochs", 50)
                mlflow.log_param("batch_size", 32)
                mlflow.log_metric("train_accuracy", train_acc)
                mlflow.log_metric("test_accuracy", test_acc)
                mlflow.log_metric("train_loss", train_loss)
                mlflow.log_metric("test_loss", test_loss)
                
                # Salvar modelo
                model_name = "disease_detection"
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                model_path = self.models_dir / f"{model_name}_{version}"
                encoder_path = self.models_dir / f"{model_name}_{version}_encoder.joblib"
                
                model.save(model_path)
                joblib.dump(label_encoder, encoder_path)
                
                # Log modelo no MLflow
                mlflow.tensorflow.log_model(model, "model")
                
                # Salvar no banco de dados
                metrics = ModelMetrics(
                    accuracy=test_acc,
                    precision=None,  # Calcular se necessário
                    recall=None,     # Calcular se necessário
                    f1_score=None    # Calcular se necessário
                )
                
                model_record = MLModel(
                    name=model_name,
                    version=version,
                    model_type="classification",
                    algorithm="tensorflow_cnn",
                    description="Modelo de detecção de doenças em plantas",
                    features=json.dumps(["image_features"]),
                    target_variable="disease_type",
                    metrics=json.dumps(metrics.__dict__),
                    training_accuracy=train_acc,
                    validation_accuracy=test_acc,
                    model_path=str(model_path),
                    encoder_path=str(encoder_path),
                    trained_at=datetime.utcnow()
                )
                
                db.session.add(model_record)
                db.session.commit()
                
                logger.info(f"Disease detection model trained successfully: {version}")
                return model_record
                
        except Exception as e:
            logger.error(f"Error training disease detection model: {e}")
            raise
    
    async def predict_crop_yield(self, culture_data: Dict[str, Any]) -> PredictionResult:
        """Prever produtividade da cultura"""
        try:
            model_key = self._get_active_model_key("crop_yield_prediction")
            
            if model_key not in self.loaded_models:
                raise ValueError("Modelo de previsão de safra não encontrado")
            
            model = self.loaded_models[model_key]
            scaler = self.scalers.get(model_key)
            
            # Preparar features
            features = [
                'area', 'soil_ph', 'soil_moisture', 'temperature_avg',
                'rainfall_total', 'fertilizer_amount', 'days_planted'
            ]
            
            feature_values = [culture_data.get(f, 0) for f in features]
            X = np.array([feature_values])
            
            # Normalizar se scaler disponível
            if scaler:
                X = scaler.transform(X)
            
            # Fazer predição
            prediction = model.predict(X)[0]
            
            # Calcular confiança (para Random Forest)
            if hasattr(model, 'predict_proba'):
                # Para classificação
                probabilities = model.predict_proba(X)[0]
                confidence = max(probabilities)
            else:
                # Para regressão, usar desvio padrão das árvores
                if hasattr(model, 'estimators_'):
                    tree_predictions = [tree.predict(X)[0] for tree in model.estimators_]
                    confidence = 1.0 - (np.std(tree_predictions) / np.mean(tree_predictions))
                else:
                    confidence = 0.8  # Valor padrão
            
            result = PredictionResult(
                prediction=float(prediction),
                confidence=float(confidence),
                model_version=model_key,
                timestamp=datetime.utcnow(),
                features_used=features,
                metadata={
                    'model_type': 'crop_yield_prediction',
                    'algorithm': 'random_forest',
                    'input_data': culture_data
                }
            )
            
            logger.info(f"Crop yield prediction: {prediction:.2f} kg/ha (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting crop yield: {e}")
            raise
    
    async def detect_plant_disease(self, image_path: str) -> PredictionResult:
        """Detectar doença em planta através de imagem"""
        try:
            model_key = self._get_active_model_key("disease_detection")
            
            if model_key not in self.loaded_models:
                raise ValueError("Modelo de detecção de doenças não encontrado")
            
            model = self.loaded_models[model_key]
            encoder = self.encoders.get(model_key)
            
            # Preprocessar imagem
            img = cv2.imread(image_path)
            img = cv2.resize(img, (224, 224))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
            
            # Fazer predição
            predictions = model.predict(img)[0]
            predicted_class = np.argmax(predictions)
            confidence = float(predictions[predicted_class])
            
            # Decodificar label
            if encoder:
                disease_name = encoder.inverse_transform([predicted_class])[0]
            else:
                disease_name = f"disease_{predicted_class}"
            
            result = PredictionResult(
                prediction=disease_name,
                confidence=confidence,
                model_version=model_key,
                timestamp=datetime.utcnow(),
                features_used=["image_features"],
                metadata={
                    'model_type': 'disease_detection',
                    'algorithm': 'tensorflow_cnn',
                    'image_path': image_path,
                    'all_probabilities': predictions.tolist()
                }
            )
            
            logger.info(f"Disease detection: {disease_name} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting plant disease: {e}")
            raise
    
    async def optimize_irrigation(self, sensor_data: Dict[str, Any]) -> PredictionResult:
        """Otimizar irrigação baseada em dados de sensores"""
        try:
            # Lógica de otimização de irrigação usando regras e ML
            soil_moisture = sensor_data.get('soil_moisture', 0)
            temperature = sensor_data.get('temperature', 0)
            humidity = sensor_data.get('humidity', 0)
            weather_forecast = sensor_data.get('weather_forecast', {})
            
            # Algoritmo de decisão para irrigação
            irrigation_needed = False
            duration_minutes = 0
            
            # Regras básicas
            if soil_moisture < 30:  # Solo muito seco
                irrigation_needed = True
                duration_minutes = 45
            elif soil_moisture < 50 and temperature > 30:  # Solo seco e calor
                irrigation_needed = True
                duration_minutes = 30
            elif soil_moisture < 40 and humidity < 40:  # Solo seco e baixa umidade
                irrigation_needed = True
                duration_minutes = 20
            
            # Ajustar baseado na previsão do tempo
            if weather_forecast.get('rain_probability', 0) > 70:
                irrigation_needed = False
                duration_minutes = 0
            
            # Calcular confiança baseada na qualidade dos dados
            data_quality = min(1.0, len([v for v in sensor_data.values() if v is not None]) / 5)
            confidence = data_quality * 0.9  # Máximo 90% para regras heurísticas
            
            result = PredictionResult(
                prediction={
                    'irrigation_needed': irrigation_needed,
                    'duration_minutes': duration_minutes,
                    'recommended_time': 'early_morning' if irrigation_needed else None
                },
                confidence=confidence,
                model_version="irrigation_optimizer_v1",
                timestamp=datetime.utcnow(),
                features_used=list(sensor_data.keys()),
                metadata={
                    'model_type': 'irrigation_optimization',
                    'algorithm': 'rule_based',
                    'sensor_data': sensor_data
                }
            )
            
            logger.info(f"Irrigation optimization: {irrigation_needed} ({duration_minutes} min)")
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing irrigation: {e}")
            raise
    
    async def analyze_market_trends(self, crop_type: str, historical_data: pd.DataFrame) -> PredictionResult:
        """Analisar tendências de mercado para uma cultura"""
        try:
            # Análise de tendências de preço
            if 'price' not in historical_data.columns or 'date' not in historical_data.columns:
                raise ValueError("Dados históricos devem conter colunas 'price' e 'date'")
            
            # Preparar dados
            data = historical_data.copy()
            data['date'] = pd.to_datetime(data['date'])
            data = data.sort_values('date')
            
            # Calcular features temporais
            data['price_ma_7'] = data['price'].rolling(window=7).mean()
            data['price_ma_30'] = data['price'].rolling(window=30).mean()
            data['price_volatility'] = data['price'].rolling(window=30).std()
            data['price_change'] = data['price'].pct_change()
            
            # Análise de tendência simples
            recent_prices = data['price'].tail(30).values
            older_prices = data['price'].tail(60).head(30).values
            
            if len(recent_prices) > 0 and len(older_prices) > 0:
                recent_avg = np.mean(recent_prices)
                older_avg = np.mean(older_prices)
                trend_direction = "up" if recent_avg > older_avg else "down"
                trend_strength = abs(recent_avg - older_avg) / older_avg
            else:
                trend_direction = "stable"
                trend_strength = 0.0
            
            # Previsão simples baseada em tendência
            current_price = data['price'].iloc[-1]
            if trend_direction == "up":
                predicted_price = current_price * (1 + trend_strength * 0.5)
            elif trend_direction == "down":
                predicted_price = current_price * (1 - trend_strength * 0.5)
            else:
                predicted_price = current_price
            
            # Calcular confiança baseada na consistência da tendência
            price_changes = data['price_change'].dropna().tail(30)
            consistency = len(price_changes[price_changes > 0]) / len(price_changes) if trend_direction == "up" else len(price_changes[price_changes < 0]) / len(price_changes)
            confidence = min(0.9, consistency)
            
            result = PredictionResult(
                prediction={
                    'current_price': float(current_price),
                    'predicted_price': float(predicted_price),
                    'trend_direction': trend_direction,
                    'trend_strength': float(trend_strength),
                    'volatility': float(data['price_volatility'].iloc[-1]) if not pd.isna(data['price_volatility'].iloc[-1]) else 0.0,
                    'recommendation': self._get_market_recommendation(trend_direction, trend_strength)
                },
                confidence=confidence,
                model_version="market_analyzer_v1",
                timestamp=datetime.utcnow(),
                features_used=['price', 'date', 'moving_averages', 'volatility'],
                metadata={
                    'model_type': 'market_analysis',
                    'algorithm': 'trend_analysis',
                    'crop_type': crop_type,
                    'data_points': len(data)
                }
            )
            
            logger.info(f"Market analysis for {crop_type}: {trend_direction} trend, {predicted_price:.2f} predicted price")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            raise
    
    def _get_market_recommendation(self, trend_direction: str, trend_strength: float) -> str:
        """Obter recomendação baseada na análise de mercado"""
        if trend_direction == "up" and trend_strength > 0.1:
            return "Considere manter ou aumentar produção. Mercado em alta."
        elif trend_direction == "down" and trend_strength > 0.1:
            return "Considere diversificar culturas. Mercado em baixa."
        else:
            return "Mercado estável. Mantenha estratégia atual."
    
    def _get_active_model_key(self, model_name: str) -> str:
        """Obter chave do modelo ativo"""
        # Buscar modelo ativo mais recente
        model = MLModel.query.filter_by(
            name=model_name,
            is_active=True
        ).order_by(MLModel.trained_at.desc()).first()
        
        if not model:
            raise ValueError(f"Nenhum modelo ativo encontrado para {model_name}")
        
        return f"{model.name}_{model.version}"
    
    async def deploy_model(self, model_id: int) -> bool:
        """Colocar modelo em produção"""
        try:
            model_record = MLModel.query.get(model_id)
            if not model_record:
                raise ValueError("Modelo não encontrado")
            
            # Desativar outros modelos do mesmo tipo
            MLModel.query.filter_by(
                name=model_record.name,
                is_production=True
            ).update({'is_production': False})
            
            # Ativar modelo atual
            model_record.is_active = True
            model_record.is_production = True
            model_record.deployed_at = datetime.utcnow()
            
            db.session.commit()
            
            # Carregar modelo na memória
            await self._load_model(model_record)
            
            logger.info(f"Model deployed to production: {model_record.name}_{model_record.version}")
            return True
            
        except Exception as e:
            logger.error(f"Error deploying model: {e}")
            return False
    
    async def retrain_model(self, model_name: str, new_data: pd.DataFrame) -> MLModel:
        """Retreinar modelo com novos dados"""
        try:
            if model_name == "crop_yield_prediction":
                return await self.train_crop_yield_model(new_data)
            elif model_name == "disease_detection":
                # Para detecção de doenças, new_data seria uma lista de (image_path, label)
                image_data = [(row['image_path'], row['disease_label']) for _, row in new_data.iterrows()]
                return await self.train_disease_detection_model(image_data)
            else:
                raise ValueError(f"Retreinamento não implementado para {model_name}")
                
        except Exception as e:
            logger.error(f"Error retraining model {model_name}: {e}")
            raise
    
    def get_model_performance(self, model_id: int) -> Dict[str, Any]:
        """Obter performance de um modelo"""
        try:
            model_record = MLModel.query.get(model_id)
            if not model_record:
                return {}
            
            metrics = json.loads(model_record.metrics) if model_record.metrics else {}
            
            return {
                'model_id': model_record.id,
                'name': model_record.name,
                'version': model_record.version,
                'model_type': model_record.model_type,
                'algorithm': model_record.algorithm,
                'training_accuracy': model_record.training_accuracy,
                'validation_accuracy': model_record.validation_accuracy,
                'test_accuracy': model_record.test_accuracy,
                'metrics': metrics,
                'is_active': model_record.is_active,
                'is_production': model_record.is_production,
                'trained_at': model_record.trained_at.isoformat(),
                'deployed_at': model_record.deployed_at.isoformat() if model_record.deployed_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return {}

# Instância global do gerenciador de modelos
model_manager = ModelManager()
```

**ETAPA 2: Sistema de Processamento de Linguagem Natural**

Crie sistema de NLP em `app/ml/nlp_processor.py`:

```python
# app/ml/nlp_processor.py
import re
import json
import spacy
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass

# Transformers para modelos pré-treinados
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

# NLTK para processamento básico
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Resultado de processamento de query"""
    intent: str
    entities: Dict[str, Any]
    confidence: float
    response: str
    suggestions: List[str]
    metadata: Dict[str, Any]

class NLPProcessor:
    """Processador de Linguagem Natural para AgroTech"""
    
    def __init__(self):
        self.nlp_pt = None
        self.sentiment_analyzer = None
        self.qa_pipeline = None
        self.tokenizer = None
        self.stemmer = PorterStemmer()
        
        # Dicionários específicos da agricultura
        self.agriculture_terms = self._load_agriculture_terms()
        self.crop_synonyms = self._load_crop_synonyms()
        self.disease_patterns = self._load_disease_patterns()
        
        # Padrões de intenção
        self.intent_patterns = self._load_intent_patterns()
        
        # Inicializar modelos
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializar modelos de NLP"""
        try:
            # Modelo spaCy para português
            self.nlp_pt = spacy.load("pt_core_news_sm")
            
            # Pipeline de análise de sentimento
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="neuralmind/bert-base-portuguese-cased",
                tokenizer="neuralmind/bert-base-portuguese-cased"
            )
            
            # Pipeline de Q&A
            self.qa_pipeline = pipeline(
                "question-answering",
                model="neuralmind/bert-base-portuguese-cased",
                tokenizer="neuralmind/bert-base-portuguese-cased"
            )
            
            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            # Fallback para funcionalidade básica
            self.nlp_pt = None
    
    def _load_agriculture_terms(self) -> Dict[str, List[str]]:
        """Carregar termos específicos da agricultura"""
        return {
            'crops': [
                'milho', 'trigo', 'soja', 'arroz', 'feijão', 'batata', 'tomate',
                'alface', 'cenoura', 'cebola', 'uva', 'maçã', 'laranja', 'limão',
                'oliveira', 'vinha', 'vinhedo', 'pomar', 'horta'
            ],
            'diseases': [
                'ferrugem', 'míldio', 'oídio', 'antracnose', 'podridão', 'mancha',
                'vírus', 'bactéria', 'fungo', 'praga', 'inseto', 'lagarta'
            ],
            'activities': [
                'plantar', 'semear', 'irrigar', 'fertilizar', 'podar', 'colher',
                'pulverizar', 'arar', 'cultivar', 'tratar', 'adubar'
            ],
            'weather': [
                'chuva', 'sol', 'vento', 'temperatura', 'umidade', 'geada',
                'seca', 'tempestade', 'granizo', 'clima'
            ],
            'soil': [
                'solo', 'terra', 'ph', 'acidez', 'alcalinidade', 'nutrientes',
                'nitrogênio', 'fósforo', 'potássio', 'matéria orgânica'
            ]
        }
    
    def _load_crop_synonyms(self) -> Dict[str, List[str]]:
        """Carregar sinônimos de culturas"""
        return {
            'milho': ['milho', 'corn', 'maíz'],
            'tomate': ['tomate', 'tomateiro', 'tomato'],
            'batata': ['batata', 'batatinha', 'potato'],
            'uva': ['uva', 'videira', 'vinha', 'grape'],
            'oliveira': ['oliveira', 'azeitona', 'olive']
        }
    
    def _load_disease_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões de doenças"""
        return {
            'fungal': [
                'manchas nas folhas', 'folhas amareladas', 'mofo', 'bolor',
                'podridão', 'ferrugem', 'míldio', 'oídio'
            ],
            'bacterial': [
                'murcha bacteriana', 'canela preta', 'podridão mole',
                'manchas oleosas'
            ],
            'viral': [
                'mosaico', 'nanismo', 'deformação das folhas',
                'amarelecimento sistêmico'
            ],
            'pest': [
                'furos nas folhas', 'lagartas', 'pulgões', 'ácaros',
                'cochonilhas', 'moscas', 'besouros'
            ]
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões de intenção"""
        return {
            'weather_query': [
                'como está o tempo', 'previsão do tempo', 'vai chover',
                'temperatura hoje', 'clima amanhã'
            ],
            'disease_diagnosis': [
                'minha planta está doente', 'folhas amarelas', 'manchas nas folhas',
                'o que é isso', 'diagnóstico', 'problema na cultura'
            ],
            'irrigation_advice': [
                'quando irrigar', 'preciso regar', 'água para plantas',
                'irrigação automática', 'sistema de rega'
            ],
            'fertilization_advice': [
                'quando fertilizar', 'que adubo usar', 'nutrientes',
                'fertilizante', 'adubação'
            ],
            'planting_advice': [
                'quando plantar', 'época de plantio', 'semear',
                'calendário agrícola', 'melhor época'
            ],
            'harvest_advice': [
                'quando colher', 'ponto de colheita', 'safra',
                'tempo de colheita', 'maturação'
            ],
            'market_info': [
                'preço', 'mercado', 'venda', 'comercialização',
                'cotação', 'valor'
            ],
            'general_help': [
                'ajuda', 'como usar', 'tutorial', 'suporte',
                'não entendi', 'explicar'
            ]
        }
    
    async def process_query(self, query: str, user_context: Dict[str, Any] = None) -> QueryResult:
        """Processar consulta em linguagem natural"""
        try:
            # Preprocessar query
            processed_query = self._preprocess_text(query)
            
            # Detectar intenção
            intent = self._detect_intent(processed_query)
            
            # Extrair entidades
            entities = self._extract_entities(processed_query)
            
            # Gerar resposta baseada na intenção
            response, confidence = await self._generate_response(
                intent, entities, processed_query, user_context
            )
            
            # Gerar sugestões
            suggestions = self._generate_suggestions(intent, entities)
            
            result = QueryResult(
                intent=intent,
                entities=entities,
                confidence=confidence,
                response=response,
                suggestions=suggestions,
                metadata={
                    'original_query': query,
                    'processed_query': processed_query,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"NLP query processed: {intent} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error processing NLP query: {e}")
            return QueryResult(
                intent="error",
                entities={},
                confidence=0.0,
                response="Desculpe, não consegui processar sua pergunta. Pode reformular?",
                suggestions=["Como está o tempo?", "Minha planta está doente", "Quando devo irrigar?"],
                metadata={'error': str(e)}
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocessar texto"""
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _detect_intent(self, query: str) -> str:
        """Detectar intenção da consulta"""
        best_intent = "general_help"
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            
            for pattern in patterns:
                # Calcular similaridade simples baseada em palavras comuns
                query_words = set(query.split())
                pattern_words = set(pattern.split())
                
                if pattern_words:
                    intersection = query_words.intersection(pattern_words)
                    similarity = len(intersection) / len(pattern_words)
                    score = max(score, similarity)
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extrair entidades da consulta"""
        entities = {}
        
        # Extrair culturas mencionadas
        crops_found = []
        for crop, synonyms in self.crop_synonyms.items():
            for synonym in synonyms:
                if synonym in query:
                    crops_found.append(crop)
        
        if crops_found:
            entities['crops'] = list(set(crops_found))
        
        # Extrair atividades agrícolas
        activities_found = []
        for activity in self.agriculture_terms['activities']:
            if activity in query:
                activities_found.append(activity)
        
        if activities_found:
            entities['activities'] = activities_found
        
        # Extrair termos meteorológicos
        weather_terms = []
        for term in self.agriculture_terms['weather']:
            if term in query:
                weather_terms.append(term)
        
        if weather_terms:
            entities['weather'] = weather_terms
        
        # Extrair números (quantidades, datas, etc.)
        numbers = re.findall(r'\d+', query)
        if numbers:
            entities['numbers'] = [int(n) for n in numbers]
        
        # Usar spaCy se disponível para extração mais avançada
        if self.nlp_pt:
            doc = self.nlp_pt(query)
            
            # Extrair entidades nomeadas
            named_entities = []
            for ent in doc.ents:
                named_entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            if named_entities:
                entities['named_entities'] = named_entities
        
        return entities
    
    async def _generate_response(self, intent: str, entities: Dict[str, Any], 
                                query: str, user_context: Dict[str, Any] = None) -> tuple[str, float]:
        """Gerar resposta baseada na intenção e entidades"""
        confidence = 0.8  # Confiança padrão
        
        if intent == "weather_query":
            response = await self._handle_weather_query(entities, user_context)
        
        elif intent == "disease_diagnosis":
            response = await self._handle_disease_diagnosis(entities, query)
        
        elif intent == "irrigation_advice":
            response = await self._handle_irrigation_advice(entities, user_context)
        
        elif intent == "fertilization_advice":
            response = await self._handle_fertilization_advice(entities, user_context)
        
        elif intent == "planting_advice":
            response = await self._handle_planting_advice(entities, user_context)
        
        elif intent == "harvest_advice":
            response = await self._handle_harvest_advice(entities, user_context)
        
        elif intent == "market_info":
            response = await self._handle_market_info(entities, user_context)
        
        else:  # general_help
            response = self._handle_general_help(query)
            confidence = 0.5
        
        return response, confidence
    
    async def _handle_weather_query(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com consultas meteorológicas"""
        # Aqui você integraria com o serviço meteorológico
        return "Baseado na previsão do IPMA, hoje teremos temperatura máxima de 28°C com possibilidade de chuva à tarde. Recomendo verificar a irrigação das suas culturas."
    
    async def _handle_disease_diagnosis(self, entities: Dict[str, Any], query: str) -> str:
        """Lidar com diagnóstico de doenças"""
        # Analisar sintomas mencionados
        symptoms = []
        for disease_type, patterns in self.disease_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    symptoms.append((disease_type, pattern))
        
        if symptoms:
            disease_type = symptoms[0][0]
            if disease_type == 'fungal':
                return "Pelos sintomas descritos, pode ser uma doença fúngica. Recomendo aplicar fungicida preventivo e melhorar a ventilação das plantas. Para diagnóstico preciso, envie uma foto da planta."
            elif disease_type == 'pest':
                return "Parece ser um problema com pragas. Verifique a presença de insetos e considere usar controle biológico ou inseticidas específicos."
        
        return "Para um diagnóstico preciso, preciso de mais informações. Pode descrever melhor os sintomas ou enviar uma foto da planta afetada?"
    
    async def _handle_irrigation_advice(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com conselhos de irrigação"""
        crops = entities.get('crops', [])
        
        if crops:
            crop = crops[0]
            return f"Para {crop}, recomendo irrigar nas primeiras horas da manhã ou final da tarde. Verifique a umidade do solo - deve estar úmido mas não encharcado. Com os sensores IoT, posso dar recomendações mais precisas."
        
        return "A irrigação ideal depende da cultura, tipo de solo e condições climáticas. Geralmente, irrigue nas primeiras horas da manhã. Quer configurar sensores de umidade para recomendações automáticas?"
    
    async def _handle_fertilization_advice(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com conselhos de fertilização"""
        return "A fertilização deve ser baseada na análise do solo e necessidades da cultura. Recomendo fazer análise de solo primeiro. Posso ajudar a interpretar os resultados e sugerir o programa de adubação ideal."
    
    async def _handle_planting_advice(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com conselhos de plantio"""
        crops = entities.get('crops', [])
        
        if crops:
            crop = crops[0]
            return f"Para {crop} em Portugal, a melhor época de plantio varia por região. Consulte o calendário agrícola na plataforma para datas específicas da sua localização."
        
        return "A época de plantio depende da cultura e região. Acesse o calendário agrícola personalizado para sua localização e culturas de interesse."
    
    async def _handle_harvest_advice(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com conselhos de colheita"""
        return "O ponto de colheita varia por cultura. Posso ajudar com indicadores visuais e temporais. Que cultura você está cultivando?"
    
    async def _handle_market_info(self, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Lidar com informações de mercado"""
        return "Acesse a seção de marketplace para preços atualizados e tendências de mercado. Posso também configurar alertas de preço para suas culturas."
    
    def _handle_general_help(self, query: str) -> str:
        """Lidar com ajuda geral"""
        return "Posso ajudar com informações sobre culturas, clima, irrigação, doenças, mercado e muito mais. Experimente perguntas como: 'Como está o tempo?', 'Quando irrigar tomates?' ou 'Preço do milho hoje'."
    
    def _generate_suggestions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """Gerar sugestões baseadas no contexto"""
        suggestions = []
        
        if intent == "weather_query":
            suggestions = [
                "Previsão para os próximos 7 dias",
                "Alertas meteorológicos",
                "Histórico de chuvas"
            ]
        
        elif intent == "disease_diagnosis":
            suggestions = [
                "Enviar foto para diagnóstico",
                "Tratamentos recomendados",
                "Prevenção de doenças"
            ]
        
        elif intent == "irrigation_advice":
            suggestions = [
                "Configurar irrigação automática",
                "Instalar sensores de umidade",
                "Calendário de irrigação"
            ]
        
        else:
            suggestions = [
                "Como está o tempo hoje?",
                "Minha planta está com manchas",
                "Quando devo irrigar?",
                "Preços do mercado"
            ]
        
        return suggestions[:3]  # Máximo 3 sugestões
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analisar sentimento do texto"""
        try:
            if self.sentiment_analyzer:
                result = self.sentiment_analyzer(text)[0]
                return {
                    'sentiment': result['label'].lower(),
                    'confidence': result['score'],
                    'text': text
                }
            else:
                # Análise simples baseada em palavras-chave
                positive_words = ['bom', 'ótimo', 'excelente', 'satisfeito', 'feliz']
                negative_words = ['ruim', 'péssimo', 'problema', 'insatisfeito', 'triste']
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    return {'sentiment': 'positive', 'confidence': 0.6, 'text': text}
                elif negative_count > positive_count:
                    return {'sentiment': 'negative', 'confidence': 0.6, 'text': text}
                else:
                    return {'sentiment': 'neutral', 'confidence': 0.5, 'text': text}
                    
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.0, 'text': text}

# Instância global do processador NLP
nlp_processor = NLPProcessor()
```

### Testes de Validação

**TESTE 1: Validação do Model Manager**
```python
# Testar treinamento de modelo
import pandas as pd

# Dados simulados para teste
culture_data = pd.DataFrame({
    'area': [1.0, 2.5, 0.5, 3.0, 1.5],
    'soil_ph': [6.5, 7.0, 6.0, 6.8, 6.2],
    'soil_moisture': [45, 60, 30, 55, 40],
    'temperature_avg': [25, 28, 22, 26, 24],
    'rainfall_total': [800, 1000, 600, 900, 750],
    'fertilizer_amount': [100, 150, 80, 120, 90],
    'days_planted': [90, 95, 85, 92, 88],
    'yield_kg_per_hectare': [5000, 6500, 3500, 6000, 4500]
})

model = await model_manager.train_crop_yield_model(culture_data)
assert model.name == "crop_yield_prediction"
```

**TESTE 2: Validação do NLP Processor**
```python
# Testar processamento de query
query = "Quando devo irrigar meus tomates?"
result = await nlp_processor.process_query(query)

assert result.intent == "irrigation_advice"
assert "tomate" in result.entities.get('crops', [])
assert result.confidence > 0.5
```

**TESTE 3: Validação de Predição**
```python
# Testar predição de safra
culture_data = {
    'area': 2.0,
    'soil_ph': 6.5,
    'soil_moisture': 50,
    'temperature_avg': 25,
    'rainfall_total': 800,
    'fertilizer_amount': 100,
    'days_planted': 90
}

prediction = await model_manager.predict_crop_yield(culture_data)
assert prediction.prediction > 0
assert prediction.confidence > 0.5
```

### Critérios de Aceitação
- Sistema de gestão de modelos ML funcionando
- Modelos de previsão de safra treinados e ativos
- Sistema de detecção de doenças operacional
- Processamento de linguagem natural em português
- API para consultas em linguagem natural
- Monitoramento de performance dos modelos

### Entregáveis Esperados
1. **Sistema de Gestão de Modelos** completo com MLOps
2. **Modelos de Machine Learning** treinados e validados
3. **Sistema de NLP** para consultas em português
4. **API de Predições** em tempo real
5. **Monitoramento** de performance dos modelos

### Informações Importantes
- Implementar versionamento de modelos robusto
- Garantir retreinamento automático com novos dados
- Estabelecer métricas de qualidade para modelos
- Configurar alertas para degradação de performance
- Implementar explicabilidade dos modelos (XAI)

---

