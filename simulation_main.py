"""
IoT-Based Appliance Usage Tracker - Simulation Main File
========================================================

This file simulates the complete IoT system:
1. Device Layer: Reads data from CSV files (simulating smart plugs)
2. Communication Layer: MQTT message publishing simulation
3. Application Layer: Cloud processor and dashboard simulation

Author: Aybüke ŞENEL
Date: 2025-12-08 
"""

import pandas as pd
import time
import json
from datetime import datetime
import os
import sys
from collections import deque

# ============================================================================
# TERMINAL COLORS AND UTILITIES
# ============================================================================
class Colors:
    """Terminal color codes for better visualization"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

# MQTT için paho-mqtt kütüphanesi (opsiyonel)
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} paho-mqtt not installed. Using simulation mode only.")
    print(f"{Colors.YELLOW}Install with: pip install paho-mqtt{Colors.RESET}\n")

# ============================================================================
# LIVE STATISTICS TRACKER
# ============================================================================
class LiveStats:
    """Tracks live statistics during simulation"""
    
    def __init__(self, device_id, device_name):
        self.device_id = device_id
        self.device_name = device_name
        self.message_count = 0
        self.total_power = 0.0
        self.max_power = 0.0
        self.min_power = float('inf')
        self.current_power = 0.0
        self.recent_powers = deque(maxlen=20)
        
    def add_data(self, power):
        """Add new data point"""
        self.message_count += 1
        self.total_power += power
        self.max_power = max(self.max_power, power)
        self.min_power = min(self.min_power, power)
        self.current_power = power
        self.recent_powers.append(power)
        
    def get_avg_power(self):
        """Calculate average power"""
        return self.total_power / self.message_count if self.message_count > 0 else 0
    
    def get_power_bar(self, width=30):
        """Generate power visualization bar"""
        if self.max_power == 0:
            return "░" * width
        
        normalized = (self.current_power / self.max_power) if self.max_power > 0 else 0
        filled = int(normalized * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar

# ============================================================================
# MQTT CLIENT (GERÇEK MQTT DESTEĞİ)
# ============================================================================
class MQTTClient:
    """Gerçek MQTT broker'a bağlanmak için client"""
    
    def __init__(self, broker_host="localhost", broker_port=1883, 
                 username=None, password=None, client_id=None):
        """
        MQTT Client oluştur
        
        Parameters:
        -----------
        broker_host : str
            MQTT broker adresi (örn: "localhost", "broker.hivemq.com", "test.mosquitto.org")
        broker_port : int
            MQTT broker portu (genellikle 1883)
        username : str, optional
            MQTT broker kullanıcı adı (gerekirse)
        password : str, optional
            MQTT broker şifresi (gerekirse)
        client_id : str, optional
            MQTT client ID (None ise otomatik oluşturulur)
        """
        if not MQTT_AVAILABLE:
            raise ImportError("paho-mqtt kütüphanesi yüklü değil. 'pip install paho-mqtt' ile yükleyin.")
        
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id or f"iot_simulator_{os.getpid()}"
        self.client = None
        self.connected = False
        
    def connect(self):
        """MQTT broker'a bağlan"""
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            
            # Authentication varsa ayarla
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Callback fonksiyonları
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            
            # Bağlan
            print(f"{Colors.BLUE}[MQTT]{Colors.RESET} Connecting to broker: {Colors.CYAN}{self.broker_host}:{self.broker_port}{Colors.RESET}")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            
            # Bağlantı bekle (max 5 saniye)
            timeout = 5
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                print(f"{Colors.GREEN}[MQTT]{Colors.RESET} Connected successfully!{Colors.RESET}\n")
            else:
                print(f"{Colors.RED}[MQTT]{Colors.RESET} Connection timeout!{Colors.RESET}\n")
                return False
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}[MQTT ERROR]{Colors.RESET} Connection failed: {str(e)}{Colors.RESET}\n")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Bağlantı callback"""
        if rc == 0:
            self.connected = True
        else:
            print(f"{Colors.RED}[MQTT]{Colors.RESET} Connection failed with code {rc}{Colors.RESET}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Bağlantı kesilme callback"""
        self.connected = False
        if rc != 0:
            print(f"{Colors.YELLOW}[MQTT]{Colors.RESET} Unexpected disconnection{Colors.RESET}")
    
    def _on_publish(self, client, userdata, mid):
        """Publish callback (mesaj gönderildiğinde çağrılır)"""
        pass  # İsteğe bağlı: publish başarılı olduğunda log
    
    def publish(self, topic, payload, qos=0, retain=False):
        """
        MQTT topic'e mesaj yayınla
        
        Parameters:
        -----------
        topic : str
            MQTT topic
        payload : dict
            JSON payload (dict olarak)
        qos : int
            Quality of Service (0, 1, veya 2)
        retain : bool
            Retain flag
        
        Returns:
        --------
        bool
            Başarılı ise True
        """
        if not self.connected:
            print(f"{Colors.RED}[MQTT ERROR]{Colors.RESET} Not connected to broker!{Colors.RESET}")
            return False
        
        try:
            json_payload = json.dumps(payload)
            result = self.client.publish(topic, json_payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
            else:
                print(f"{Colors.RED}[MQTT ERROR]{Colors.RESET} Publish failed with code {result.rc}{Colors.RESET}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}[MQTT ERROR]{Colors.RESET} Publish error: {str(e)}{Colors.RESET}")
            return False
    
    def disconnect(self):
        """MQTT broker'dan bağlantıyı kes"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print(f"{Colors.BLUE}[MQTT]{Colors.RESET} Disconnected{Colors.RESET}")

# ============================================================================
# MQTT PUBLISH FUNCTIONS (SIMÜLASYON VE GERÇEK)
# ============================================================================
def fake_mqtt_publish(topic, payload, stats, verbose=True, show_json=True):
    """
    Simulates MQTT publish operation
    
    In a real system, this would send data to an MQTT broker.
    Here, we simulate the publish operation by processing the payload.
    """
    power = payload.get("power", 0.0)
    timestamp = payload.get("timestamp", "")
    
    # Update statistics
    stats.add_data(power)
    
    # JSON mesajını formatla
    json_message = json.dumps(payload, indent=2)
    
    # Display message (every 100 messages for performance or always if verbose)
    if verbose or show_json:
        print(f"\n{Colors.MAGENTA}{'='*80}")
        print(f"{Colors.MAGENTA}[MQTT PUBLISH - SIMULATION]{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Topic:{Colors.RESET} {Colors.CYAN}{topic}{Colors.RESET}")
        print(f"{Colors.BOLD}Publishing to MQTT:{Colors.RESET} topic={Colors.CYAN}{topic}{Colors.RESET}")
        
        if show_json:
            print(f"\n{Colors.BOLD}JSON Message:{Colors.RESET}")
            print(f"{Colors.YELLOW}{json_message}{Colors.RESET}")
        
        avg_power = stats.get_avg_power()
        power_bar = stats.get_power_bar()
        
        print(f"\n{Colors.BOLD}Power Info:{Colors.RESET}")
        print(f"  Current: {Colors.CYAN}{power:>8.2f} W{Colors.RESET} | "
              f"Avg: {Colors.YELLOW}{avg_power:>8.2f} W{Colors.RESET} | "
              f"Msg: {Colors.BLUE}{stats.message_count:>6}{Colors.RESET}")
        print(f"  [{Colors.GREEN}{power_bar}{Colors.RESET}]")
        print(f"{Colors.MAGENTA}{'='*80}{Colors.RESET}\n")

def real_mqtt_publish(mqtt_client, topic, payload, stats, verbose=True, show_json=True):
    """
    Gerçek MQTT broker'a mesaj yayınla
    
    Parameters:
    -----------
    mqtt_client : MQTTClient
        Bağlı MQTT client
    topic : str
        MQTT topic
    payload : dict
        JSON payload
    stats : LiveStats
        İstatistikler
    verbose : bool
        Detaylı çıktı göster
    show_json : bool
        JSON mesajını göster
    """
    power = payload.get("power", 0.0)
    timestamp = payload.get("timestamp", "")
    
    # Update statistics
    stats.add_data(power)
    
    # JSON mesajını formatla
    json_message = json.dumps(payload, indent=2)
    
    # Gerçek MQTT'ye gönder
    success = mqtt_client.publish(topic, payload, qos=0)
    
    # Display message
    if verbose or show_json:
        status_color = Colors.GREEN if success else Colors.RED
        status_text = "✓ PUBLISHED" if success else "✗ FAILED"
        
        print(f"\n{Colors.MAGENTA}{'='*80}")
        print(f"{Colors.MAGENTA}[MQTT PUBLISH - REAL]{Colors.RESET} {status_color}{status_text}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Topic:{Colors.RESET} {Colors.CYAN}{topic}{Colors.RESET}")
        print(f"{Colors.BOLD}Publishing to MQTT:{Colors.RESET} topic={Colors.CYAN}{topic}{Colors.RESET}")
        print(f"{Colors.BOLD}Broker:{Colors.RESET} {Colors.CYAN}{mqtt_client.broker_host}:{mqtt_client.broker_port}{Colors.RESET}")
        
        if show_json:
            print(f"\n{Colors.BOLD}JSON Message:{Colors.RESET}")
            print(f"{Colors.YELLOW}{json_message}{Colors.RESET}")
        
        avg_power = stats.get_avg_power()
        power_bar = stats.get_power_bar()
        
        print(f"\n{Colors.BOLD}Power Info:{Colors.RESET}")
        print(f"  Current: {Colors.CYAN}{power:>8.2f} W{Colors.RESET} | "
              f"Avg: {Colors.YELLOW}{avg_power:>8.2f} W{Colors.RESET} | "
              f"Msg: {Colors.BLUE}{stats.message_count:>6}{Colors.RESET}")
        print(f"  [{Colors.GREEN}{power_bar}{Colors.RESET}]")
        print(f"{Colors.MAGENTA}{'='*80}{Colors.RESET}\n")

# ============================================================================
# APPLICATION LAYER - MQTT SUBSCRIBER (Communication Layer'dan veri alır)
# ============================================================================
class ApplicationLayer:
    """
    Application Layer - MQTT'den subscribe edip JSON ile işler
    
    Bu katman:
    1. Communication Layer'dan (MQTT broker) mesajları subscribe eder
    2. JSON formatındaki mesajları parse eder
    3. Verileri işler ve analiz eder
    """
    
    def __init__(self, mqtt_client=None, topic_filter="home/appliance/+/power"):
        """
        Application Layer oluştur
        
        Parameters:
        -----------
        mqtt_client : MQTTClient, optional
            MQTT client (gerçek MQTT için)
        topic_filter : str
            Subscribe edilecek topic pattern (örn: "home/appliance/+/power")
        """
        self.received_messages = []
        self.processed_count = 0
        self.device_stats = {}
        self.mqtt_client = mqtt_client
        self.topic_filter = topic_filter
        self.subscribed = False
        
    def subscribe_to_mqtt(self):
        """MQTT broker'dan mesajları subscribe et"""
        if not self.mqtt_client or not self.mqtt_client.connected:
            print(f"{Colors.YELLOW}[APPLICATION LAYER]{Colors.RESET} No MQTT client. Using simulation mode.{Colors.RESET}")
            return False
        
        try:
            # MQTT callback fonksiyonlarını ayarla
            self.mqtt_client.client.on_message = self._on_mqtt_message
            
            # Topic'e subscribe ol
            self.mqtt_client.client.subscribe(self.topic_filter, qos=0)
            self.subscribed = True
            
            print(f"{Colors.GREEN}[APPLICATION LAYER]{Colors.RESET} Subscribed to topic: {Colors.CYAN}{self.topic_filter}{Colors.RESET}\n")
            return True
        except Exception as e:
            print(f"{Colors.RED}[APPLICATION LAYER ERROR]{Colors.RESET} Subscribe failed: {str(e)}{Colors.RESET}")
            return False
    
    def _on_mqtt_message(self, client, userdata, msg):
        """
        MQTT mesajı geldiğinde çağrılır (callback)
        
        Bu fonksiyon Communication Layer'dan (MQTT broker) gelen mesajları alır
        """
        try:
            # MQTT'den gelen mesajı JSON olarak parse et
            topic = msg.topic
            json_payload = msg.payload.decode('utf-8')
            payload = json.loads(json_payload)
            
            # Application Layer'da işle
            self.process_json_message(topic, payload)
            
        except json.JSONDecodeError as e:
            print(f"{Colors.RED}[APPLICATION LAYER ERROR]{Colors.RESET} JSON parse error: {str(e)}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[APPLICATION LAYER ERROR]{Colors.RESET} Message processing error: {str(e)}{Colors.RESET}")
    
    def process_json_message(self, topic, payload, verbose=True):
        """
        Communication Layer'dan gelen JSON mesajını işle
        
        Bu fonksiyon:
        1. JSON formatındaki mesajı alır (Communication Layer'dan)
        2. Verileri parse eder
        3. İstatistikleri hesaplar
        4. Application Layer'da işler
        
        Parameters:
        -----------
        topic : str
            MQTT topic
        payload : dict
            JSON payload (Communication Layer'dan gelen)
        verbose : bool
            Detaylı çıktı göster
        """
        try:
            device_id = payload.get("device_id", "unknown")
            timestamp = payload.get("timestamp", "")
            power = payload.get("power", 0.0)
            
            # İstatistikleri güncelle
            if device_id not in self.device_stats:
                self.device_stats[device_id] = {
                    "message_count": 0,
                    "total_power": 0.0,
                    "max_power": 0.0,
                    "min_power": float('inf'),
                }
            
            stats = self.device_stats[device_id]
            stats["message_count"] += 1
            stats["total_power"] += power
            stats["max_power"] = max(stats["max_power"], power)
            stats["min_power"] = min(stats["min_power"], power)
            
            self.received_messages.append({
                "device_id": device_id,
                "timestamp": timestamp,
                "power": power,
                "topic": topic
            })
            self.processed_count += 1
            
            # Display processing info
            if verbose and self.processed_count % 100 == 0:
                avg_power = stats["total_power"] / stats["message_count"]
                print(f"\n{Colors.GREEN}{'='*80}")
                print(f"{Colors.GREEN}[APPLICATION LAYER]{Colors.RESET} Processing message #{self.processed_count:,}")
                print(f"{Colors.GREEN}{'='*80}{Colors.RESET}")
                print(f"{Colors.BOLD}Received from Communication Layer (MQTT):{Colors.RESET}")
                print(f"  Topic: {Colors.CYAN}{topic}{Colors.RESET}")
                print(f"  Device: {Colors.CYAN}{device_id}{Colors.RESET}")
                print(f"  Power: {Colors.YELLOW}{power:.2f} W{Colors.RESET}")
                print(f"  Timestamp: {Colors.BLUE}{timestamp}{Colors.RESET}")
                print(f"\n{Colors.BOLD}JSON Payload (from Communication Layer):{Colors.RESET}")
                print(f"{Colors.YELLOW}{json.dumps(payload, indent=2)}{Colors.RESET}")
                print(f"\n{Colors.BOLD}Statistics:{Colors.RESET}")
                print(f"  Avg Power: {Colors.YELLOW}{avg_power:.2f} W{Colors.RESET}")
                print(f"  Max Power: {Colors.RED}{stats['max_power']:.2f} W{Colors.RESET}")
                print(f"  Min Power: {Colors.BLUE}{stats['min_power']:.2f} W{Colors.RESET}")
                print(f"  Messages: {Colors.CYAN}{stats['message_count']}{Colors.RESET}")
                print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
                
        except Exception as e:
            print(f"{Colors.RED}[APPLICATION LAYER ERROR]{Colors.RESET} Processing failed: {str(e)}{Colors.RESET}")

# ============================================================================
# CLOUD PROCESSOR SIMULATION (Backward compatibility)
# ============================================================================
class CloudProcessor(ApplicationLayer):
    """
    Backward compatibility için - ApplicationLayer'ın eski adı
    """
    pass

# ============================================================================
# LIVE DASHBOARD SIMULATION
# ============================================================================
def print_dashboard(stats, processor):
    """
    Displays live dashboard with real-time statistics
    
    This simulates a web-based dashboard that shows:
    - Device information
    - Real-time power consumption
    - Statistics and trends
    """
    clear_screen()
    
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}")
    print(f"LIVE IoT SIMULATION DASHBOARD - {stats.device_name}")
    print("="*80 + Colors.RESET)
    
    avg_power = stats.get_avg_power()
    power_bar = stats.get_power_bar(50)
    
    print(f"\n{Colors.BOLD}Device Information:{Colors.RESET}")
    print(f"  Device ID: {Colors.CYAN}{stats.device_id}{Colors.RESET}")
    print(f"  Device Name: {Colors.CYAN}{stats.device_name}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Real-time Statistics:{Colors.RESET}")
    print(f"  Current Power:     {Colors.GREEN}{stats.current_power:>10.2f} W{Colors.RESET}")
    print(f"  Average Power:     {Colors.YELLOW}{avg_power:>10.2f} W{Colors.RESET}")
    print(f"  Maximum Power:     {Colors.RED}{stats.max_power:>10.2f} W{Colors.RESET}")
    print(f"  Minimum Power:     {Colors.BLUE}{stats.min_power:>10.2f} W{Colors.RESET}")
    print(f"  Messages Processed: {Colors.CYAN}{stats.message_count:>10,}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Power Visualization:{Colors.RESET}")
    print(f"  [{Colors.GREEN}{power_bar}{Colors.RESET}]")
    print(f"  0{' ' * 24}Max: {stats.max_power:.2f}W")
    
    print(f"\n{Colors.BOLD}Cloud Processor:{Colors.RESET}")
    print(f"  Messages Processed: {Colors.GREEN}{processor.processed_count:,}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Recent Power Values:{Colors.RESET}")
    recent = list(stats.recent_powers)[-10:]
    if recent:
        recent_str = " | ".join([f"{Colors.CYAN}{p:>6.2f}W{Colors.RESET}" for p in recent])
        print(f"  {recent_str}")
    
    print(f"\n{Colors.YELLOW}{'─'*80}{Colors.RESET}")
    print(f"{Colors.MAGENTA}Processing MQTT messages...{Colors.RESET}")

# ============================================================================
# DEVICE SIMULATION
# ============================================================================
def simulate_device(device_name, csv_file, device_id, topic_prefix, 
                    sample_size=None, publish_rate=10000.0, mqtt_client=None):
    """
    Simulates a single IoT device
    
    Parameters:
    -----------
    device_name : str
        Human-readable device name
    csv_file : str
        Path to CSV file containing device data
    device_id : str
        Unique device identifier
    topic_prefix : str
        MQTT topic prefix (e.g., "home/appliance")
    sample_size : int or None
        Number of records to simulate (None = all records)
    publish_rate : float
        Messages per second (higher = faster simulation)
    
    Returns:
    --------
    CloudProcessor
        Processor instance with processed messages
    """
    
    try:
        # Load dataset
        print(f"{Colors.BLUE}[LOADING]{Colors.RESET} Reading {csv_file}...")
        df = pd.read_csv(csv_file, parse_dates=["timestamp"])
        print(f"{Colors.GREEN}[LOADED]{Colors.RESET} {len(df):,} records loaded\n")
        
        # Initialize statistics and Application Layer
        stats = LiveStats(device_id, device_name)
        # Application Layer oluştur (Communication Layer'dan MQTT ile veri alacak)
        processor = ApplicationLayer(mqtt_client=mqtt_client, topic_filter=f"{topic_prefix}/+/power")
        
        # Eğer gerçek MQTT kullanıyorsak, Application Layer'ı subscribe et
        if mqtt_client and mqtt_client.connected:
            processor.subscribe_to_mqtt()
        
        # Prepare data
        if sample_size is None:
            sample_df = df
            total_records = len(df)
            print(f"{Colors.GREEN}[INFO]{Colors.RESET} Using ALL {total_records:,} records from dataset")
        else:
            sample_df = df.head(sample_size)
            total_records = len(sample_df)
            print(f"{Colors.GREEN}[INFO]{Colors.RESET} Using {total_records:,} records from dataset")
        
        print(f"{Colors.BOLD}Starting data stream simulation...{Colors.RESET}\n")
        
        # Calculate estimated time
        estimated_seconds = total_records / publish_rate
        estimated_minutes = estimated_seconds / 60
        
        if estimated_minutes >= 1:
            print(f"{Colors.YELLOW}Estimated time: ~{estimated_minutes:.1f} minutes{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Estimated time: ~{estimated_seconds:.0f} seconds{Colors.RESET}")
        
        print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.RESET}\n")
        time.sleep(2)
        
        # Dashboard update frequency
        dashboard_update_interval = 100 if total_records > 1000 else 1
        
        # TÜM VERİLER İÇİN BAŞLANGIÇ ZAMANI
        start_time = time.time()
        
        # Simulation loop
        for i, row in sample_df.iterrows():
            # Create MQTT payload
            payload = {
                "device_id": device_id,
                "timestamp": row["timestamp"].isoformat(),
                "power": float(row["power"])
            }
            
            # MQTT topic
            topic = f"{topic_prefix}/{device_id}/power"
            
            # Update dashboard periodically
            if (i + 1) % dashboard_update_interval == 0 or (i + 1) == total_records:
                print_dashboard(stats, processor)
            
            # TÜM VERİLER İÇİN OPTİMİZE EDİLMİŞ ÇIKTI AYARLARI
            # Büyük dosyalar için her mesajda değil, belirli aralıklarla göster
            verbose = False  # Tüm veriler için False (her mesajda çıktı olmasın)
            
            # JSON gösterimi: İlk mesaj, sonra her 1000 mesajda bir, ve son mesaj
            show_json = (
                stats.message_count == 1 or  # İlk mesaj
                stats.message_count % 1000 == 0 or  # Her 1000 mesajda bir
                (i + 1) == total_records  # Son mesaj
            )
            
            # Önemli mesajlar için özet göster (her 100 mesajda bir)
            show_summary = stats.message_count % 100 == 0
            
            # ================================================================
            # DEVICE LAYER → COMMUNICATION LAYER (MQTT Publish)
            # ================================================================
            # Device Layer'dan Communication Layer'a MQTT ile gönder
            if mqtt_client and mqtt_client.connected:
                # Gerçek MQTT broker'a gönder (Communication Layer)
                real_mqtt_publish(mqtt_client, topic, payload, stats, verbose=show_summary, show_json=show_json)
            else:
                # Simülasyon modu (Communication Layer simülasyonu)
                fake_mqtt_publish(topic, payload, stats, verbose=show_summary, show_json=show_json)
            
            # ================================================================
            # COMMUNICATION LAYER → APPLICATION LAYER (MQTT Subscribe + JSON)
            # ================================================================
            # Eğer gerçek MQTT kullanıyorsak, Application Layer zaten subscribe ile alacak
            # Simülasyon modunda ise direkt işle
            if not (mqtt_client and mqtt_client.connected):
                # Simülasyon modu: Communication Layer'dan Application Layer'a direkt geçiş
                # Tüm veriler için: her 1000 mesajda bir veya önemli mesajlarda göster
                app_verbose = show_summary or stats.message_count % 1000 == 0
                processor.process_json_message(topic, payload, verbose=app_verbose)
            
            # TÜM VERİLER İÇİN İLERLEME GÖSTERİMİ (her 100 kayıtta bir)
            if (i + 1) % 100 == 0 or (i + 1) == total_records:
                progress = ((i + 1) / total_records) * 100
                progress_bar_length = 50
                filled = int(progress_bar_length * progress / 100)
                bar = "█" * filled + "░" * (progress_bar_length - filled)
                
                # İstatistiklerle birlikte göster
                avg_power = stats.get_avg_power()
                elapsed_time = time.time() - start_time
                if (i + 1) % 100 == 0:
                    print(f"\r{Colors.CYAN}[PROGRESS]{Colors.RESET} [{bar}] {progress:.1f}% | "
                          f"Mesaj: {i+1:,}/{total_records:,} | "
                          f"Ortalama Güç: {avg_power:.2f}W | "
                          f"Süre: {elapsed_time:.1f}s", 
                          end="", flush=True)
            
            # Realistic publish rate delay
            time.sleep(1.0 / publish_rate)
        
        # Final dashboard ve özet
        print_dashboard(stats, processor)
        
        # TÜM VERİLER İÇİN DETAYLI FİNAL ÖZET
        total_time = time.time() - start_time
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*80}")
        print(f"✓ SIMULATION COMPLETE FOR {device_name.upper()}!")
        print(f"{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}Final Statistics:{Colors.RESET}")
        print(f"  Total Records Processed: {Colors.CYAN}{total_records:,}{Colors.RESET}")
        print(f"  Total Messages: {Colors.CYAN}{stats.message_count:,}{Colors.RESET}")
        print(f"  Average Power: {Colors.YELLOW}{stats.get_avg_power():.2f} W{Colors.RESET}")
        print(f"  Max Power: {Colors.RED}{stats.max_power:.2f} W{Colors.RESET}")
        print(f"  Min Power: {Colors.BLUE}{stats.min_power:.2f} W{Colors.RESET}")
        print(f"  Total Time: {Colors.MAGENTA}{total_time:.2f} seconds{Colors.RESET}")
        print(f"  Processing Rate: {Colors.CYAN}{total_records/total_time:.0f} records/second{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*80}{Colors.RESET}\n")
        
        return processor
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Simulation interrupted by user.{Colors.RESET}")
        return None
    except FileNotFoundError:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} File not found: {csv_file}")
        return None
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Simulation failed: {str(e)}")
        return None

# ============================================================================
# MAIN SIMULATION FUNCTION
# ============================================================================
def main():
    """
    Main simulation function
    
    IoT Sistem Mimarisi:
    ====================
    1. DEVICE LAYER: Dataset'ten veri okur (Smart Plug simülasyonu)
       ↓ (MQTT Publish)
    2. COMMUNICATION LAYER: MQTT Broker (mesajları iletir)
       ↓ (MQTT Subscribe + JSON)
    3. APPLICATION LAYER: JSON mesajlarını alır ve işler
    
    Simulates the complete IoT system with multiple devices:
    - Reads data from CSV files (device layer)
    - Publishes MQTT messages (communication layer)
    - Subscribes to MQTT and processes JSON messages (application layer)
    - Displays live dashboard
    """
    
    # Clear screen and show header
    clear_screen()
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}")
    print("IoT-BASED APPLIANCE USAGE TRACKER - SIMULATION")
    print("="*80 + Colors.RESET)
    print(f"\n{Colors.GREEN}Starting IoT Simulation System...{Colors.RESET}")
    print(f"{Colors.BLUE}Simulating: ESP32 Smart Plugs + MQTT + Cloud Processor{Colors.RESET}\n")
    
    # ========================================================================
    # MQTT MODU SEÇİMİ
    # ========================================================================
    # ⚠️ ÖNEMLİ: Şu anda SIMÜLASYON MODU aktif (gerçek MQTT kullanmıyor)
    # Gerçek MQTT kullanmak için aşağıdaki ayarları yapın:
    USE_REAL_MQTT = False  # True = Gerçek MQTT, False = Simülasyon (ŞU AN: False = Simülasyon)
    
    # MQTT Broker Ayarları (USE_REAL_MQTT=True ise)
    # Seçenek 1: Public Broker (kolay - internet gerekir)
    MQTT_BROKER_HOST = "broker.hivemq.com"  # veya "test.mosquitto.org"
    # Seçenek 2: Yerel Broker (daha iyi - Mosquitto kurulumu gerekir)
    # MQTT_BROKER_HOST = "localhost"  # Yerel Mosquitto için
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = None  # Gerekirse kullanıcı adı
    MQTT_PASSWORD = None  # Gerekirse şifre
    
    mqtt_client = None
    
    if USE_REAL_MQTT:
        if not MQTT_AVAILABLE:
            print(f"{Colors.RED}[ERROR]{Colors.RESET} paho-mqtt not installed!")
            print(f"{Colors.YELLOW}Install with: pip install paho-mqtt{Colors.RESET}")
            print(f"{Colors.YELLOW}Switching to simulation mode...{Colors.RESET}\n")
            USE_REAL_MQTT = False
        else:
            try:
                mqtt_client = MQTTClient(
                    broker_host=MQTT_BROKER_HOST,
                    broker_port=MQTT_BROKER_PORT,
                    username=MQTT_USERNAME,
                    password=MQTT_PASSWORD
                )
                if mqtt_client.connect():
                    print(f"{Colors.GREEN}✓ Using REAL MQTT broker{Colors.RESET}\n")
                else:
                    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} MQTT connection failed. Switching to simulation mode...{Colors.RESET}\n")
                    mqtt_client = None
            except Exception as e:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} MQTT setup failed: {str(e)}{Colors.RESET}")
                print(f"{Colors.YELLOW}Switching to simulation mode...{Colors.RESET}\n")
                mqtt_client = None
    
    if not USE_REAL_MQTT or not mqtt_client:
        print(f"{Colors.BLUE}ℹ Using SIMULATION mode (no real MQTT broker){Colors.RESET}\n")
        print(f"{Colors.BLUE}  Device Layer → Communication Layer (MQTT simülasyonu) → Application Layer (JSON){Colors.RESET}\n")
    else:
        print(f"{Colors.GREEN}✓ Real MQTT Architecture:{Colors.RESET}")
        print(f"{Colors.GREEN}  Device Layer → MQTT Publish → Communication Layer (MQTT Broker) → MQTT Subscribe → Application Layer (JSON){Colors.RESET}\n")
    
    # Simulation parameters
    # TÜM VERİLER İÇİN AYARLAR (fridge_207.csv ve vacuum_254.csv'nin tamamı)
    SAMPLE_SIZE = None  # None = TÜM kayıtlar (fridge_207 ve vacuum_254 dosyalarının tamamı)
    PUBLISH_RATE = 10000.0  # Messages per second (10000 = hızlı simülasyon, tüm veriler için)
    
    # Device configurations
    devices = [
        {
            "name": "Buzdolabı",
            "csv_file": "fridge_207.csv",
            "device_id": "fridge_207",
            "topic_prefix": "home/appliance"
        },
        {
            "name": "Süpürge",
            "csv_file": "vacuum_254.csv",
            "device_id": "vacuum_254",
            "topic_prefix": "home/appliance"
        }
    ]
    
    all_processors = []
    
    # Simulate each device
    for device in devices:
        processor = simulate_device(
            device["name"],
            device["csv_file"],
            device["device_id"],
            device["topic_prefix"],
            SAMPLE_SIZE,
            PUBLISH_RATE,
            mqtt_client=mqtt_client
        )
        
        if processor:
            all_processors.append(processor)
        
        # Pause between devices
        if device != devices[-1]:
            print(f"\n{Colors.CYAN}Preparing next device simulation...{Colors.RESET}\n")
            time.sleep(2)
    
    # TÜM VERİLER İÇİN GENEL ÖZET
    clear_screen()
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}")
    print("SIMULATION COMPLETE - FINAL SUMMARY")
    print("TÜM VERİLER İŞLENDİ (fridge_207.csv + vacuum_254.csv)")
    print("="*80 + Colors.RESET)
    
    total_messages = sum(len(p.received_messages) for p in all_processors)
    print(f"\n{Colors.BOLD}Genel İstatistikler:{Colors.RESET}")
    print(f"  Simüle Edilen Cihaz Sayısı: {Colors.GREEN}{len(all_processors)}{Colors.RESET}")
    print(f"  Toplam İşlenen Mesaj: {Colors.BLUE}{total_messages:,}{Colors.RESET}")
    
    # Her cihaz için detaylı özet
    print(f"\n{Colors.BOLD}Cihaz Bazında Detaylar:{Colors.RESET}")
    for i, processor in enumerate(all_processors):
        device = devices[i]
        device_stats = processor.device_stats.get(device['device_id'], {})
        
        if device_stats:
            avg_power = device_stats['total_power'] / device_stats['message_count'] if device_stats['message_count'] > 0 else 0
            print(f"\n  {Colors.BOLD}{device['name']} ({device['device_id']}):{Colors.RESET}")
            print(f"    Toplam Mesaj: {Colors.CYAN}{device_stats['message_count']:,}{Colors.RESET}")
            print(f"    Ortalama Güç: {Colors.YELLOW}{avg_power:.2f} W{Colors.RESET}")
            print(f"    Maksimum Güç: {Colors.RED}{device_stats['max_power']:.2f} W{Colors.RESET}")
            print(f"    Minimum Güç: {Colors.BLUE}{device_stats['min_power']:.2f} W{Colors.RESET}")
        else:
            print(f"\n  {Colors.BOLD}{device['name']} ({device['device_id']}):{Colors.RESET}")
            print(f"    Mesaj Sayısı: {Colors.CYAN}{len(processor.received_messages):,}{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*80}")
    print("✓ TÜM VERİLER BAŞARIYLA İŞLENDİ!")
    print("  - fridge_207.csv: TAMAMEN İŞLENDİ")
    print("  - vacuum_254.csv: TAMAMEN İŞLENDİ")
    print("="*80 + Colors.RESET + "\n")
    
    # MQTT bağlantısını kapat
    if mqtt_client:
        mqtt_client.disconnect()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Simulation interrupted by user.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")

