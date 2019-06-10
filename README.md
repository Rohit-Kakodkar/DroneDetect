## Introduction

This project aims at building a data pipeline to collect data from IoT sensors in Unmanned Autonomous Vehicles (UAV). For the use case presented here, the pipeline collects data from gyrometric sensors, barometric altimeter readings and wind speeds from sensors onboard drones. This data is used to detect anomalies and automatically log sensor data close to anomalous events.

## Motivation

It is estimated that delivery drone logistic and transportation market is expected to grown to $29bn by year 2027 while by the year 2025 we are expected to see ~8 million Autonomous vehicles on the streets. With such high number of UAVs, events such as Uber crash need to be analyzed to understand and improve decisions leading to such accidents. However, increasing amounts of UAVs leads to exponential growth in data collected (~11TB/vehicle per day). Filtering this data to detect anomalous (unexpected) events becomes increasingly time consuming and compute expensive. This architecture addresses this case by detecting anomalous behavior real-time and recording the sensor data close the the event so that it is easily accessible to Data Scientists and AI engineers.
