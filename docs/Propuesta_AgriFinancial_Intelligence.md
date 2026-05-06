# Propuesta AgTech: Agri-Financial Intelligence Hybrid

## 1. Visión General
El proyecto busca resolver la desconexión actual entre la gestión operativa/financiera y el riesgo ambiental en el sector agropecuario. No se trata solo de registrar "qué pasó", sino de proyectar "qué pasará" con la rentabilidad ante cambios externos.

## 2. El Concepto Híbrido (1 + 7)
La solución integra la gestión de márgenes brutos (ERP) con inteligencia climática predictiva.
* **Componente Financiero (7):** Control de costos por lote, insumos, labores y precios de mercado.
* **Componente Predictivo (1):** Modelos de IA que analizan datos satelitales e históricos para prever riesgos climáticos.
* **Sinergia:** El sistema recalcula automáticamente los márgenes proyectados si detecta un riesgo climático inminente (ej. estrés hídrico), permitiendo decisiones reactivas inmediatas.

## 3. Análisis de Mercado
* **Jugadores Actuales:** Albor (robusto/contable), Agropro (gestión de procesos), Auravant/SIMA (monitoreo biológico/satelital).
* **Oportunidad:** Existe un hueco en la integración fluida entre el estado biológico del cultivo y su impacto financiero directo en tiempo real.

## 4. Definición del MVP (Producto Mínimo Viable)
Para validar la hipótesis rápidamente, el MVP se centrará en una **Calculadora de Márgenes Dinámica**:
1. **Tablero de Costos por Lote:** Carga simplificada de inversiones (semillas, gasoil, agroquímicos).
2. **Precios en Vivo:** Integración con APIs de mercados (ej. Matba Rofex) para valuación de stocks.
3. **Monitor de Riesgo Climático:** Visualización de estado hídrico por lote mediante NDVI/Datos satelitales.
4. **Simulador "What-If":** Herramienta para modelar escenarios de rentabilidad basados en variaciones de rinde o precio.

## 5. Stack Tecnológico Sugerido
* **Frontend:** Flutter (Mobile-first con capacidades Offline-first).
* **Backend:** .NET 10 en arquitectura de Microservicios.
* **Infraestructura:** AWS (Lambdas para procesamiento, RDS para transacciones).
* **IA/Data:** Python para modelos predictivos y procesamiento de imágenes.

## 6. Diferenciador Clave
La clave de la adopción será la **Baja Fricción**. El sistema debe incluir:
* **OCR con IA:** Carga de facturas e insumos mediante fotos para evitar la carga manual.
* **Interoperabilidad:** APIs abiertas para conectar con maquinaria y sensores existentes.
