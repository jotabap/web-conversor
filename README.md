# Web Conversor - Azure Static Web App

Aplicación web completa para conversión de archivos Excel/CSV a diferentes formatos, desplegada en Azure Static Web Apps con Azure Functions para el backend.

## Arquitectura

- **Frontend**: Vue.js 3 + Vite + TailwindCSS
- **Backend**: Azure Functions (Python 3.11)
- **Deployment**: Azure Static Web Apps
- **AI Integration**: Azure OpenAI para análisis de datos

## Funcionalidades

### Conversiones Disponibles
1. **Excel a JSON**: Convierte archivos Excel (.xlsx) a formato JSON
2. **JSON a Excel**: Convierte datos JSON a archivo Excel
3. **Excel a SQL**: Genera consultas SQL CREATE TABLE e INSERT basadas en datos Excel
4. **Formatos soportados**: Lista todos los formatos disponibles

### Endpoints API (Azure Functions)
- `GET /` - Información de la aplicación
- `GET /health` - Estado de salud del servicio
- `GET /info` - Información detallada del servicio
- `GET /formats` - Formatos soportados
- `POST /excel-to-json` - Conversión Excel a JSON
- `POST /json-to-excel` - Conversión JSON a Excel
- `POST /excel-to-sql` - Conversión Excel a SQL

## Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+
- Python 3.11+
- Azure Functions Core Tools
- Cuenta de Azure (para deployment)

### Setup Local

1. **Instalar dependencias del frontend**:
```bash
npm install
```

2. **Instalar dependencias del backend (Azure Functions)**:
```bash
cd api
pip install -r requirements.txt
```

3. **Configurar variables de entorno** (api/local.settings.json):
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "tu_endpoint_opcional",
    "AZURE_OPENAI_API_KEY": "tu_key_opcional",
    "AZURE_OPENAI_API_VERSION": "2024-02-01",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4"
  }
}
```

### Desarrollo Local

1. **Ejecutar frontend**:
```bash
npm run dev
```

2. **Ejecutar Azure Functions**:
```bash
cd api
func start
```

### Testing

Usar el archivo `test_data.json` incluido para probar las conversiones.

## Deployment en Azure

La aplicación está configurada para deployment automático en Azure Static Web Apps con:
- **Frontend**: Buildeo automático con Vite
- **Backend**: Azure Functions integradas
- **Configuración**: `staticwebapp.config.json` para routing

### Estructura del Proyecto Limpio

```
/
├── api/                    # Azure Functions (Backend)
│   ├── function_app.py    # Función principal con todos los endpoints
│   ├── host.json         # Configuración Azure Functions
│   ├── requirements.txt  # Dependencias Python
│   ├── core/            # Configuración
│   ├── models/          # Modelos Pydantic
│   ├── services/        # Lógica de negocio
│   └── utils/           # Utilidades
├── src/                # Frontend Vue.js
├── public/             # Assets estáticos
├── package.json        # Dependencias Node.js
├── vite.config.js     # Configuración Vite
├── tailwind.config.js # Configuración TailwindCSS
├── staticwebapp.config.json # Configuración Azure Static Web Apps
└── test_data.json     # Datos de prueba
```

## Tecnologías

- **Frontend**: Vue 3, Vite, TailwindCSS
- **Backend**: Azure Functions, Python 3.11
- **Data Processing**: pandas, openpyxl, numpy
- **AI**: Azure OpenAI (opcional)
- **Cloud**: Azure Static Web Apps, Azure Functions

## Migración Completada

Este proyecto fue migrado exitosamente de FastAPI a Azure Functions para optimizar costos y compatibilidad con Azure Static Web Apps.