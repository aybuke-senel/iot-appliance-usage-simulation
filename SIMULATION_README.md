# IoT-Based Appliance Usage Tracker - Simulation

## Overview

This simulation models the end-to-end data flow of an IoT-based appliance usage tracking system.

The system follows a three-layer architecture:

1. **Device Layer**: Reads data from CSV files (simulating smart plug sensor data)
2. **Communication Layer**: Simulates MQTT message publishing
3. **Application Layer**: Processes incoming data and displays a live dashboard

---

## Main File

- [**`simulation_main.py`**](./simulation_main.py)

##  Usage

### Requirements
```bash
pip install pandas numpy
```

### Run the Simulation
```bash
python3 simulation_main.py
```

## Configuration

You can adjust the following parameters in [`simulation_main.py`](./simulation_main.py):

```python
SAMPLE_SIZE = None      # Limits the number of records (None = full dataset)
PUBLISH_RATE = 10000.0  # Controls how fast messages are sent
```

## Components

### 1. MQTT Publish Simulation
```python
def fake_mqtt_publish(topic, payload, stats, verbose=True):
```

**Behavior:**
- Topic format: `home/appliance/{device_id}/power`
- JSON payload structure: `{"device_id": "...", "timestamp": "...", "power": ...}`
- Message rate controlled via PUBLISH_RATE

### 2. Cloud Processing
```python
class CloudProcessor:
```

**Behavior:**
- Receives messages
- Parses JSON payload
- Updates statistics
- Prepares data for further processing

### 3. Live Dashboard
```python
def print_dashboard(stats, processor):
```

**Displays:**
- Device information
- Real-time power consumption
- Average / max / min values
- Processed message count
- Power visualization

### 4. Statistics Tracking
```python
class LiveStats:
```

**Tracks:**
- Total messages
- Power statistics
- Min / max values
- Recent measurements

## Simulation Flow

```
1. Read data from CSV
   ↓
2. For each record:
   ├─ Create MQTT payload
   ├─ Simulate publish
   ├─ Cloud processing simulation
   ├─ Update statistics
   └─ Update dashboard periodically
   ↓
3. Display final dashboard
   ↓
4. Display final summary
```

## Project Usage

### Paper

1. [**`Main Simulation File`**](./simulation_main.py)
   - Contains the entire simulation logic
   - Well-documented
   - Suitable format for the project

2. **Simulation Components**:
   - `fake_mqtt_publish()`: MQTT publishing simulation
   - `CloudProcessor`: Cloud processing simulation
   - `LiveStats`: Statistics tracking
   - `print_dashboard()`: Dashboard display

### Usage in Our Presentation

To record the simulation, I captured the terminal output:
```bash
script -a simulation_output.txt python3 simulation_main.py

```

## Terminal Outputs
- Live dashboard updates
- Progress tracking
- Real-time statistics
- MQTT message logs (optional)

## Technical Details

### Data Format
- **Input**: CSV files (`fridge_207.csv`, `vacuum_254.csv`)
- **Format**: `timestamp`, `power` columns
- **Timestamp**: ISO format datetime

### MQTT Message Format
```json
{
  "device_id": "fridge_207",
  "timestamp": "2024-01-01T00:00:00",
  "power": 45.5
}
```

### Performance Optimizations
- Dashboard updates are performed periodically for large datasets
- Message logs are shown by sampling, not for every message
- Progress bar is updated every 100 records

## References

This simulation represents the following real system components:

1. **ESP32 Smart Plugs**: Data read from CSV files
2. **MQTT Broker**: fake_mqtt_publish() function
3. **Cloud Server**: CloudProcessor class
4. **Web Dashboard**: print_dashboard() function

## Notes

- This is a simulation (no real MQTT broker required)
- All communication is handled within Python
- The structure is designed to resemble a real IoT system
- Can be extended to a real-world implementation

## Academic Context

This simulation code is described in the "**Proposed Methodology**" section of the project as follows:

> "The simulation represents a three-layer architecture: 
(1) the device layer reads sensor data from CSV files, (2) the communication layer simulates message publishing using the MQTT protocol, and (3) the application layer performs cloud-based message processing and live dashboard visualization."
> 
The simulation code is available in [`simulation_main.py`](./simulation_main.py) and can be used to demonstrate the technical implementation of the system.


