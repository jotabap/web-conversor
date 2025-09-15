// API utilities for backend communication
const API_BASE_URL = 'http://localhost:7071/api';

// API endpoints
export const API_ENDPOINTS = {
  EXCEL_TO_JSON: '/convert/excel-to-json',
  JSON_TO_EXCEL: '/convert/json-to-excel',
  EXCEL_TO_SQL: '/convert/excel-to-sql',
  FORMATS: '/convert/formats',
  HEALTH: '/health',
  INFO: '/info'
};

// API client class
export class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async convertExcelToJSON(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add optional parameters
    if (options.useAI) formData.append('use_ai', 'true');
    if (options.confidence) formData.append('min_confidence', options.confidence);
    
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.EXCEL_TO_JSON}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  async convertJSONToExcel(jsonData, options = {}) {
    const formData = new FormData();
    
    // Handle different JSON input types
    if (typeof jsonData === 'string') {
      formData.append('json_data', jsonData);
    } else if (jsonData instanceof File) {
      formData.append('file', jsonData);
    } else {
      formData.append('json_data', JSON.stringify(jsonData));
    }
    
    // Add optional parameters
    if (options.filename) formData.append('filename', options.filename);
    if (options.useAI) formData.append('use_ai', 'true');
    
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.JSON_TO_EXCEL}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    // Return blob for file download
    return await response.blob();
  }

  async convertExcelToSQL(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add optional parameters
    if (options.tableName) formData.append('table_name', options.tableName);
    if (options.useAI) formData.append('use_ai', 'true');
    
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.EXCEL_TO_SQL}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  async getSupportedFormats() {
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.FORMATS}`);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  async checkHealth() {
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.HEALTH}`);
    return await response.json();
  }

  async getAppInfo() {
    const response = await fetch(`${this.baseURL}${API_ENDPOINTS.INFO}`);
    return await response.json();
  }
}

// Export default instance
export const apiClient = new APIClient();

// File validation utilities
export const FileValidators = {
  isExcelFile(file) {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
      'application/vnd.ms-excel', // .xls
      'text/csv' // .csv
    ];
    
    return validTypes.includes(file.type) || file.name.match(/\.(xlsx?|csv)$/i);
  },

  isJSONFile(file) {
    return file.type === 'application/json' || file.name.endsWith('.json');
  },

  getFileSize(file) {
    const sizeInKB = (file.size / 1024).toFixed(2);
    const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
    
    return file.size < 1024 * 1024 
      ? `${sizeInKB} KB` 
      : `${sizeInMB} MB`;
  }
};
