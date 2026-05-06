# Proyecto Agro: Ecosistema de Inteligencia Agrícola y Climática (V2)

## 1. Visión General
Este proyecto es una solución integral que combina la gestión operativa-financiera del agro con un motor de inteligencia climática desacoplado. Está diseñado para escalar desde una infraestructura local mínima hasta una arquitectura cloud robusta.

## 2. Componentes del Proyecto

### A. Agri-Financial Intelligence (Módulo 7 + 1)
Gestión de márgenes brutos dinámicos integrados con riesgo ambiental.
* **Documentación:** [Propuesta_AgriFinancial_Intelligence.md](./Propuesta_AgriFinancial_Intelligence.md)
* **Estrategia de Negocio:** [Modelo_Negocio_Agro_Detallado.md](./Modelo_Negocio_Agro_Detallado.md)
* **Objetivo:** Optimizar la rentabilidad del productor mediante datos en tiempo real y servicios financieros.

### B. Climate-as-a-Service - CaaS (Módulo de Inteligencia Climática)
Motor de predicción hiper-local con capacidad de suplantar la interpretación meteorológica manual.
* **Documentación:** [Estrategia_Climate_as_a_Service.md](./Estrategia_Climate_as_a_Service.md)
* **Objetivo:** Proveer insights de impacto climático para múltiples industrias.

### C. Estrategia de Negocio y Monetización General
Análisis de mercado, competencia y modelo de ingresos resumido.
* **Documentación:** [Plan_Negocio_y_Monetizacion.md](./Plan_Negocio_y_Monetizacion.md)

## 3. Hoja de Ruta Técnica (Modo "A Pulmón")
Para la etapa inicial, se prioriza la ejecución local:
1. **Local Ingestion:** Scripts en Python para descarga de datos a disco local.
2. **Abstracted Storage:** Implementación de un `FileStorageManager` que permita alternar entre `LocalFileSystem` y `AWS S3`.
3. **Core API:** .NET 10 corriendo en contenedores locales o servidores on-premise.
