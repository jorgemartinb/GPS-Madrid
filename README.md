# 📍 Sistema de Navegación GPS - Madrid

Este proyecto es un sistema de navegación inteligente desarrollado para la asignatura de **Matemática Discreta**. Implementa algoritmos clásicos de teoría de grafos para calcular rutas óptimas en el callejero oficial de la ciudad de Madrid.

## 🚀 Características
- **Modelado de Red Vial:** Construcción de un grafo dirigido a partir de datos de OpenStreetMap (OSMnx) y el callejero oficial del Ayuntamiento de Madrid.
- **Algoritmos desde Cero:** Implementación propia de Dijkstra, Prim y Kruskal sin librerías externas para la lógica del cálculo.
- **Modos de Ruta:**
  - **Ruta más corta:** Optimiza la distancia en metros.
  - **Ruta más rápida:** Basada en límites de velocidad por tipo de vía.
  - **Optimización de Semáforos:** Modelo probabilístico ($p=0.8$) que añade retrasos de 30s en cruces.
- **Instrucciones de Voz:** Generación de indicaciones detalladas (giros a la izquierda/derecha y distancias).

## 🛠️ Tecnologías
- **Python 3.x**
- **NetworkX:** Gestión y análisis de grafos.
- **OSMnx:** Recuperación de datos geoespaciales.
- **Pandas:** Procesamiento de datos del callejero.

## 📋 Requisitos e Instalación
1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   pip install -r requirements_gps.txt
3. Descarga de Datos Obligatoria: Debido al peso del archivo, el dataset direcciones.csv no se incluye en este repositorio. Debes descargarlo del portal oficial del Ayuntamiento de Madrid y guardarlo en la carpeta raíz del proyecto:
   Descargar callejero oficial (Ayuntamiento de Madrid)
