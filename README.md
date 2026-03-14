# IoT-Based Appliance Usage Tracker – Simulation System

A Python-based IoT simulation that processes large-scale appliance power consumption data and mimics real-time device communication using MQTT messaging.

This project demonstrates how smart home devices can stream energy usage data to the cloud for monitoring, aggregation, and analytics.

-----

## Developers
- Aybüke Şenel
- Faika Nur Köse
- Onur Mustafa Tekin

-----

## Project Purpose

The goal of this project is to simulate an IoT architecture for tracking household appliance energy consumption.

Before the simulation stage, the dataset was explored and cleaned manually. SQL queries were used to filter records, remove null values, and select the most relevant appliance datasets for the simulation.

The system:
- reads appliance sensor logs from CSV files
- simulates IoT devices
- publishes real-time messages via MQTT
- processes data on the cloud side
- generates usage statistics and analytics

-----

## Features

- IoT device simulation
- Real-time MQTT messaging
- Streaming data processing
- Power consumption analysis
- Appliance-level statistics
- Scalable architecture
- Large dataset support

-----

## Tech Stack

- Python
- Pandas
- SQL (dataset filtering & preprocessing)
- MQTT (paho-mqtt)
- CSV time-series data processing
- Simulation-based architecture
- Power BI (data visualization)


-----

## System Architecture

Device Layer → MQTT Broker → Cloud Processor → Analytics Dashboard

- Virtual devices read sensor logs
- Messages are streamed to the broker
- Cloud layer aggregates and analyzes data
- Results are visualized and monitored

-----

## Dataset

This project uses the public dataset:

Household Appliances Power Consumption Dataset  
Source (Kaggle):  
https://www.kaggle.com/datasets/ecoco2/household-appliances-power-consumption

Due to size limitations, the dataset is **not included** in this repository.

The simulation was tested using selected appliance logs (e.g., fridge and vacuum cleaner).  
Any similar CSV time-series dataset can be used to run the code.

-----

## How to Run

Install required libraries:
```bash
pip install pandas paho-mqtt
```

Run the simulation:
```bash
python simulation_main.py
```
