# Matrix AI Converter - Azure Functions

Neural Network-powered Excel to JSON conversion service migrado a **Azure Functions** para deployment en **Azure Static Web Apps** con costo cero.

## 🚀 Migración Completada

### ✅ Endpoints Migrados

| Endpoint Original (FastAPI) | Azure Function | Estado |
|------------------------------|----------------|--------|
| `GET /` | `root()` | ✅ |
| `GET /health` | `health_check()` | ✅ |
| `GET /info` | `app_info()` | ✅ |
| `POST /convert/excel-to-json` | `convert_excel_to_json()` | ✅ |
| `POST /convert/json-to-excel` | `convert_json_to_excel()` | ✅ |
| `POST /convert/excel-to-sql` | `convert_excel_to_sql()` | ✅ |
| `GET /convert/formats` | `get_formats()` | ✅ |

### 🔧 Características

- **Azure Functions v2** (Python 3.11)
- **Procesamiento AI** con Azure OpenAI
- **Conversiones soportadas:**
  - Excel/CSV → JSON
  - JSON → Excel  
  - Excel/CSV → SQL
- **Formato de archivos:** .xlsx, .xls, .csv
- **Tamaño máximo:** 10MB por archivo

## 📁 Estructura del Proyecto

```
Web-Conversor/
├── api/                          # Azure Functions Backend
│   ├── function_app.py          # Funciones principales
│   ├── host.json                # Configuración Functions
│   ├── local.settings.json      # Variables locales
│   ├── requirements.txt         # Dependencias Python
│   ├── .funcignore             # Archivos ignorados
│   ├── core/
│   │   └── config.py           # Configuración (adaptada)
│   ├── services/
│   │   ├── converter_service.py # Servicio de conversión (adaptado)
│   │   ├── ai_service.py       # Servicio AI
│   │   └── azure_openai_service.py
│   ├── models/
│   │   ├── requests.py         # Modelos de request
│   │   └── responses.py        # Modelos de response
│   └── utils/
│       ├── logger.py           # Logger (adaptado)
│       └── exceptions.py       # Excepciones
├── src/                         # Frontend Vue.js
├── staticwebapp.config.json     # Configuración Azure SWA
└── README.md
```

## 🛠️ Desarrollo Local

### Prerrequisitos

1. **Python 3.11+**
2. **Azure Functions Core Tools v4**
3. **Node.js 18+** (para el frontend)

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <repository-url>
   cd Web-Conversor
   ```

2. **Configurar Azure Functions:**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   Editar `api/local.settings.json`:
   ```json
   {
     "Values": {
       "AZURE_OPENAI_ENDPOINT": "tu-endpoint",
       "AZURE_OPENAI_API_KEY": "tu-api-key",
       "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4"
     }
   }
   ```

4. **Instalar frontend:**
   ```bash
   cd ../
   npm install
   ```

### Ejecutar Localmente

1. **Iniciar Azure Functions:**
   ```bash
   cd api
   func start
   ```
   Funciones disponibles en: `http://localhost:7071/api/`

2. **Iniciar Frontend (en otra terminal):**
   ```bash
   npm run dev
   ```
   Frontend disponible en: `http://localhost:5173`

### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/` | Root endpoint |
| GET | `/api/health` | Health check |
| GET | `/api/info` | Info de la aplicación |
| GET | `/api/convert/formats` | Formatos soportados |
| POST | `/api/convert/excel-to-json` | Excel/CSV → JSON |
| POST | `/api/convert/json-to-excel` | JSON → Excel |
| POST | `/api/convert/excel-to-sql` | Excel/CSV → SQL |

## 🚀 Deployment en Azure

### Azure Static Web Apps (Costo Cero)

1. **Crear Azure Static Web App:**
   ```bash
   az staticwebapp create \\
     --name "matrix-ai-converter" \\
     --resource-group "tu-resource-group" \\
     --location "East US 2" \\
     --source "https://github.com/tu-usuario/Web-Conversor" \\
     --branch "main" \\
     --app-location "/" \\
     --api-location "api" \\
     --output-location "dist"
   ```

2. **Configurar Variables de Entorno en Azure:**
   ```bash
   az staticwebapp appsettings set \\
     --name "matrix-ai-converter" \\
     --setting-names \\
       AZURE_OPENAI_ENDPOINT="tu-endpoint" \\
       AZURE_OPENAI_API_KEY="tu-api-key" \\
       AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
   ```

3. **GitHub Actions:** Se configurará automáticamente para CI/CD

### Configuración de Azure OpenAI

Para usar las funciones AI, necesitas:

1. **Crear Azure OpenAI Service**
2. **Desplegar modelo GPT-4**
3. **Configurar las variables:**
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|------------------|
| `AZURE_OPENAI_ENDPOINT` | Endpoint de Azure OpenAI | "" |
| `AZURE_OPENAI_API_KEY` | API Key de Azure OpenAI | "" |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Nombre del deployment | "gpt-4" |
| `MAX_FILE_SIZE` | Tamaño máximo de archivo (bytes) | "10485760" |
| `DEFAULT_CONFIDENCE_THRESHOLD` | Umbral de confianza AI | "0.8" |
| `LOG_LEVEL` | Nivel de logging | "INFO" |

### Límites

- **Tamaño máximo de archivo:** 10MB
- **Formatos soportados:** .xlsx, .xls, .csv
- **Timeout de Azure Functions:** 10 minutos
- **Azure Static Web Apps:** Tier gratuito

## 🧪 Testing

```bash
# Probar funciones localmente
cd api
func start

# Probar endpoints
curl http://localhost:7071/api/health
curl -X POST http://localhost:7071/api/convert/excel-to-json \\
  -F "file=@test_data.xlsx"
```

## 📝 Cambios Principales de la Migración

### De FastAPI a Azure Functions

1. **Estructura:** Router-based → Function-based
2. **Archivos:** `UploadFile` → `bytes` directos
3. **Configuración:** Settings class → Azure App Settings
4. **Logging:** Custom logger → Azure Functions logging
5. **Dependency Injection:** FastAPI DI → Manual instantiation

### Beneficios

- ✅ **Costo cero** con Azure Static Web Apps
- ✅ **Auto-scaling** serverless
- ✅ **CI/CD** automático con GitHub Actions
- ✅ **Menor latencia** al eliminar servidor dedicado
- ✅ **Mejor disponibilidad** distribuida globalmente

## 🆘 Troubleshooting

### Errores Comunes

1. **Function timeout:** Verificar `host.json` timeout configuration
2. **Missing dependencies:** Ejecutar `pip install -r requirements.txt`
3. **CORS issues:** Verificar `staticwebapp.config.json`
4. **AI service errors:** Verificar Azure OpenAI credentials

### Logs

```bash
# Ver logs de Functions localmente
func start --verbose

# Ver logs en Azure
az monitor log-analytics query \\
  --workspace "tu-workspace" \\
  --analytics-query "traces | where message contains 'Matrix'"
```

## 📞 Soporte

Para issues y soporte:
- Crear issue en GitHub
- Revisar logs de Azure Functions
- Verificar configuración de Azure OpenAI

---

**Migración completada exitosamente** ✅  
**FastAPI → Azure Functions** 🚀