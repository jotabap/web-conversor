<template>
  <div class="matrix-bg min-h-screen flex flex-col items-center justify-center text-green-400 font-mono relative overflow-hidden">
    <!-- Matrix rain effect background -->
    <div class="matrix-rain"></div>
    
    <!-- Scanlines effect -->
    <div class="scanlines"></div>
    
    <!-- Main terminal -->
    <div class="terminal-container relative z-10">
      <!-- Terminal header -->
      <div class="terminal-header">
        <div class="terminal-buttons">
          <span class="terminal-button red"></span>
          <span class="terminal-button yellow"></span>
          <span class="terminal-button green"></span>
        </div>
        <div class="terminal-title">AI CONVERTER v2.1</div>
      </div>
      
      <!-- Terminal content -->
      <div class="terminal-content">
        <!-- Logo with glitch effect -->
        <div class="logo-container mb-6">
          <div class="matrix-logo glitch" data-text="⚡ NEURAL NET ⚡">
            ⚡ NEURAL NET ⚡
          </div>
        </div>

        <!-- Terminal text -->
        <div class="terminal-text">
          <p class="mb-4 whitespace-pre-line typing-text">{{ displayedText }}</p>
          <span v-if="showCursor" class="cursor">█</span>
        </div>

        <!-- Options Menu -->
        <div v-if="showOptions" class="options-container mt-6">
          <div class="options-grid">
            <button
              v-for="option in options"
              :key="option.value"
              @click="selectOption(option.value)"
              class="option-button"
              :class="{ 'selected': selectedOption === option.value }"
            >
              <div class="option-number">[{{ option.value }}]</div>
              <div class="option-label">{{ option.label }}</div>
              <div class="option-description">{{ option.description }}</div>
            </button>
          </div>
          <div class="options-hint">
            <span class="blink">&gt;</span> PRESS 1-4 OR CLICK TO SELECT PROTOCOL
          </div>
        </div>

        <!-- Upload interface -->
        <div v-if="showUpload" class="upload-container mt-6">
          <div class="upload-border">
            <div class="upload-inner">
              <input
                type="file"
                ref="fileInput"
                class="file-input"
                @change="handleFileSelect"
              />
              <div class="upload-text">
                <span class="upload-icon">📁</span>
                <span>DRAG FILE OR CLICK TO SELECT</span>
              </div>
            </div>
          </div>
          
          <button 
            class="upload-button mt-4" 
            @click="processFile"
            :disabled="isProcessing || (!selectedFile && selectedOption !== 4)"
            :class="{ 'processing': isProcessing }"
          >
            <span class="button-text" v-if="!isProcessing">&gt; EXECUTE CONVERSION</span>
            <span class="button-text" v-else>&gt; PROCESSING... {{ isProcessing ? '⚡' : '' }}</span>
          </button>
        </div>

        <!-- Results Area -->
        <div v-if="conversionResult" class="results-container mt-6">
          <div class="results-header">
            <span class="results-title">⚡ CONVERSION RESULTS ⚡</span>
          </div>
          <div class="results-content">
            <!-- Processing Mode Info -->
            <div class="processing-mode-info mb-4" v-if="conversionResult?.metadata?.ai_usage">
              <div class="mode-badge" :class="getModeClass(conversionResult?.metadata?.ai_usage?.processing_mode)">
                <span class="mode-icon">{{ getModeIcon(conversionResult?.metadata?.ai_usage?.ai_used) }}</span>
                <span class="mode-text">{{ getModeText(conversionResult?.metadata?.ai_usage?.processing_mode) }}</span>
              </div>
              <div class="user-explanation">
                {{ conversionResult?.metadata?.ai_usage?.user_friendly_explanation || '' }}
              </div>
            </div>

            <!-- Main Stats -->
            <div class="result-stats">
              <div class="stat-item">
                <span class="stat-label">STATUS:</span>
                <span class="stat-value success">{{ conversionResult?.status || 'Unknown' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">RECORDS:</span>
                <span class="stat-value">{{ conversionResult?.metadata?.record_count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">CONFIDENCE:</span>
                <span class="stat-value" :class="getConfidenceClass(conversionResult?.metadata?.confidence || 0)">
                  {{ conversionResult?.metadata?.confidence || 0 }}%
                </span>
              </div>
              <div class="stat-item">
                <span class="stat-label">TIME:</span>
                <span class="stat-value">{{ conversionResult?.metadata?.processing_time || 'N/A' }}</span>
              </div>
            </div>

            <!-- File Info -->
            <div class="file-info-section mt-4" v-if="conversionResult?.metadata?.file_info">
              <div class="section-title">📁 FILE ANALYSIS</div>
              <div class="file-details">
                <div class="detail-row">
                  <span class="detail-label">FILENAME:</span>
                  <span class="detail-value">{{ conversionResult?.metadata?.file_info?.filename || 'N/A' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">SIZE:</span>
                  <span class="detail-value">{{ conversionResult?.metadata?.file_info?.size ? formatFileSize(conversionResult.metadata.file_info.size) : 'N/A' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">COLUMNS:</span>
                  <span class="detail-value">{{ conversionResult?.metadata?.columns?.length || 0 }}</span>
                </div>
              </div>
            </div>

            <!-- AI Analysis Details -->
            <div class="ai-analysis-section mt-4" v-if="conversionResult?.metadata?.ai_analysis">
              <div class="section-title">🤖 NEURAL ANALYSIS</div>
              <div class="analysis-grid">
                <div class="analysis-item">
                  <span class="analysis-label">PROCESSING:</span>
                  <span class="analysis-value">{{ conversionResult?.metadata?.ai_analysis?.analysis_type?.toUpperCase() || 'N/A' }}</span>
                </div>
                <div class="analysis-item" v-if="conversionResult?.metadata?.ai_analysis?.detected_patterns?.length > 0">
                  <span class="analysis-label">PATTERNS:</span>
                  <span class="analysis-value">{{ conversionResult.metadata.ai_analysis.detected_patterns.join(', ') }}</span>
                </div>
              </div>
              
              <!-- Issues and Recommendations -->
              <div v-if="conversionResult?.metadata?.ai_usage?.issues_detected?.length > 0" class="issues-section mt-3">
                <div class="issues-title">⚠️ ISSUES DETECTED:</div>
                <ul class="issues-list">
                  <li v-for="issue in conversionResult.metadata.ai_usage.issues_detected" :key="issue">
                    {{ formatIssue(issue) }}
                  </li>
                </ul>
              </div>

              <div v-if="conversionResult?.metadata?.ai_analysis?.recommendations?.length > 0" class="recommendations-section mt-3">
                <div class="recommendations-title">💡 RECOMMENDATIONS:</div>
                <ul class="recommendations-list">
                  <li v-for="rec in conversionResult.metadata.ai_analysis.recommendations" :key="rec">
                    {{ rec }}
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- AI Usage Details -->
            <div class="ai-usage-details mt-4" v-if="conversionResult?.metadata?.ai_usage">
              <div class="section-title">🔬 AI PROCESSING DETAILS</div>
              <div class="ai-usage-grid">
                <div class="usage-item">
                  <span class="usage-label">AI ENABLED:</span>
                  <span class="usage-value" :class="conversionResult.metadata.ai_usage.ai_used ? 'ai-active' : 'ai-inactive'">
                    {{ conversionResult.metadata.ai_usage.ai_used ? 'YES' : 'NO' }}
                  </span>
                </div>
                <div class="usage-item">
                  <span class="usage-label">PROCESSING MODE:</span>
                  <span class="usage-value mode-value">{{ conversionResult.metadata.ai_usage.processing_mode?.toUpperCase() || 'DETERMINISTIC' }}</span>
                </div>
                <div class="usage-item" v-if="conversionResult.metadata.ai_usage.trigger_reason">
                  <span class="usage-label">TRIGGER REASON:</span>
                  <span class="usage-value">{{ conversionResult.metadata.ai_usage.trigger_reason }}</span>
                </div>
                <div class="usage-item" v-if="conversionResult.metadata.ai_usage.ai_improvements?.length > 0">
                  <span class="usage-label">AI IMPROVEMENTS:</span>
                  <span class="usage-value">{{ conversionResult.metadata.ai_usage.ai_improvements.length }} applied</span>
                </div>
              </div>
              
              <!-- AI Improvements List -->
              <div v-if="conversionResult?.metadata?.ai_usage?.ai_improvements?.length > 0" class="ai-improvements mt-3">
                <div class="improvements-title">🚀 AI IMPROVEMENTS APPLIED:</div>
                <ul class="improvements-list">
                  <li v-for="improvement in conversionResult.metadata.ai_usage.ai_improvements" :key="improvement">
                    {{ improvement }}
                  </li>
                </ul>
              </div>
              
              <!-- Technical Details -->
              <div v-if="conversionResult?.metadata?.ai_usage?.technical_details" class="technical-details-ai mt-3">
                <div class="technical-title">⚙️ TECHNICAL DETAILS:</div>
                <pre class="technical-content">{{ conversionResult.metadata.ai_usage.technical_details }}</pre>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="result-actions mt-6">
              <button class="download-button" @click="downloadResult">
                <span>📥 DOWNLOAD</span>
              </button>
              <button class="preview-button" @click="togglePreview">
                <span>👁️ {{ showPreview ? 'HIDE' : 'PREVIEW' }} DATA</span>
              </button>
              <button class="details-button" @click="toggleDetails">
                <span>🔍 {{ showDetails ? 'HIDE' : 'SHOW' }} DETAILS</span>
              </button>
            </div>
            
            <!-- Preview Area -->
            <div v-if="showPreview" class="preview-area mt-4">
              <div class="preview-header">JSON PREVIEW ({{ conversionResult?.metadata?.record_count || 0 }} records):</div>
              <pre class="json-preview">{{ formatJsonPreview(conversionResult?.data) }}</pre>
            </div>

            <!-- Technical Details -->
            <div v-if="showDetails" class="technical-details mt-4">
              <div class="details-header">TECHNICAL DETAILS:</div>
              <div class="details-content">
                <div class="detail-section" v-if="conversionResult?.metadata?.ai_analysis?.column_types">
                  <div class="detail-section-title">Column Types:</div>
                  <div class="column-types-grid">
                    <div v-for="(type, column) in conversionResult.metadata.ai_analysis.column_types" 
                         :key="column" 
                         class="column-type-item">
                      <span class="column-name">{{ column }}:</span>
                      <span class="column-type" :class="getTypeClass(type)">{{ type?.toUpperCase() || 'UNKNOWN' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Mission Control Section -->
        <div v-if="showMissionControl" class="mission-control-container mt-6">
          <div class="mission-header">
            <div class="mission-title">⚡ MISSION ACCOMPLISHED ⚡</div>
            <div class="mission-subtitle">DATA SUCCESSFULLY PROCESSED</div>
            <div class="mission-status">AWAITING NEXT INSTRUCTIONS...</div>
          </div>
          
          <div class="mission-content">
            <div class="mission-stats">
              <div class="mission-stat">
                <span class="stat-icon">✅</span>
                <span class="stat-text">CONVERSION COMPLETE</span>
              </div>
              <div class="mission-stat">
                <span class="stat-icon">📊</span>
                <span class="stat-text">{{ conversionResult?.metadata?.record_count || 0 }} RECORDS PROCESSED</span>
              </div>
              <div class="mission-stat">
                <span class="stat-icon">⚡</span>
                <span class="stat-text">NEURAL NETWORK ACTIVE</span>
              </div>
            </div>

            <div class="mission-actions">
              <button class="mission-button primary" @click="startNewMission">
                <span class="button-icon">🔄</span>
                <span class="button-label">NEW MISSION</span>
                <span class="button-desc">Process another file</span>
              </button>
              
              <button class="mission-button secondary" @click="changeProtocol">
                <span class="button-icon">🔀</span>
                <span class="button-label">CHANGE PROTOCOL</span>
                <span class="button-desc">Select different conversion</span>
              </button>
              
              <button class="mission-button accent" @click="downloadAndExit">
                <span class="button-icon">📥</span>
                <span class="button-label">DOWNLOAD & EXIT</span>
                <span class="button-desc">Save results and disconnect</span>
              </button>
            </div>

            <div class="mission-footer">
              <div class="matrix-signature">
                <span class="signature-text">MATRIX AI CONVERTER v2.1</span>
                <span class="signature-status">● NEURAL NETWORK ONLINE</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System info -->
    <div class="system-info">
      <div>SYSTEM STATUS: ONLINE</div>
      <div>NEURAL NETWORK: ACTIVE</div>
      <div>ENCRYPTION: ENABLED</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const fullText = `> INITIALIZING NEURAL NETWORK...
> CONNECTING TO MATRIX...
> CONNECTION ESTABLISHED

WELCOME TO THE MATRIX CONVERTER

╔══════════════════════════════════════╗
║  SELECT CONVERSION PROTOCOL:         ║
╠══════════════════════════════════════╣
║  [1] EXCEL → JSON TRANSFORMATION    ║
║  [2] JSON → EXCEL RECONSTRUCTION    ║
║  [3] EXCEL → SQL GENERATION         ║
║  [4] SUPPORTED FORMATS ANALYSIS     ║
╚══════════════════════════════════════╝

> AWAITING PROTOCOL SELECTION...
> USE MOUSE CLICK OR PRESS 1-4 KEYS`;

const displayedText = ref("");
const showUpload = ref(false);
const showCursor = ref(true);
const fileInput = ref(null);
const selectedOption = ref(null);
const showOptions = ref(false);
const selectedFile = ref(null);
const isProcessing = ref(false);
const conversionResult = ref(null);
const showPreview = ref(false);
const showDetails = ref(false);
const showMissionControl = ref(false);

// Backend configuration
const API_BASE_URL = 'http://localhost:7071/api'; // Azure Functions backend

const options = [
  { value: 1, label: "EXCEL → JSON TRANSFORMATION", description: "Convert Excel files to JSON format" },
  { value: 2, label: "JSON → EXCEL RECONSTRUCTION", description: "Convert JSON data to Excel format" },
  { value: 3, label: "EXCEL → SQL GENERATION", description: "Generate SQL CREATE TABLE and INSERT statements from Excel" },
  { value: 4, label: "SUPPORTED FORMATS ANALYSIS", description: "Display all supported file formats and features" }
];

// Handle option selection
const selectOption = (optionValue) => {
  selectedOption.value = optionValue;
  const option = options.find(opt => opt.value === optionValue);
  
  // Update displayed text to show selection
  displayedText.value += `\n\n> PROTOCOL [${optionValue}] SELECTED
> ${option.label}
> STATUS: ${option.description}
> AWAITING DATA INPUT...`;
  
  showOptions.value = false;
  showUpload.value = true;
};

// Keyboard event handler
const handleKeyPress = (event) => {
  const key = event.key;
  if (['1', '2', '3', '4'].includes(key) && showOptions.value) {
    const optionValue = parseInt(key);
    selectOption(optionValue);
  }
};

// Cursor blinking effect
onMounted(() => {
  // Typing effect
  let i = 0;
  const typingInterval = setInterval(() => {
    if (i < fullText.length) {
      displayedText.value += fullText[i];
      i++;
    } else {
      clearInterval(typingInterval);
      showOptions.value = true;
    }
  }, 50); // Faster typing for better effect

  // Cursor blinking
  const cursorInterval = setInterval(() => {
    showCursor.value = !showCursor.value;
  }, 500);

  // Add keyboard event listener
  document.addEventListener('keydown', handleKeyPress);
  
  // Cleanup function
  onUnmounted(() => {
    clearInterval(cursorInterval);
    document.removeEventListener('keydown', handleKeyPress);
  });
});

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    // Validate file type for Excel conversion
    if (selectedOption.value === 1) {
      const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel', // .xls
        'text/csv' // .csv
      ];
      
      if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx?|csv)$/i)) {
        displayedText.value += `\n> ERROR: INVALID FILE FORMAT
> EXPECTED: .xlsx, .xls, or .csv
> RECEIVED: ${file.name}
> PLEASE SELECT A VALID EXCEL FILE`;
        return;
      }
    }
    
    selectedFile.value = file;
    displayedText.value += `\n> FILE LOADED: ${file.name}
> FILE SIZE: ${(file.size / 1024).toFixed(2)} KB
> FILE TYPE: ${file.type || 'Unknown'}
> STATUS: READY FOR AI ANALYSIS`;
  }
};

// API call to backend
const callBackendAPI = async (file, option) => {
  // Special case for option 4 (formats) - no file upload needed
  if (option === 4) {
    const response = await fetch(`${API_BASE_URL}/convert/formats`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
  
  // For other options, use form data with file upload
  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversion_type', option.toString());
  
  try {
    displayedText.value += `\n> ESTABLISHING CONNECTION TO AI SERVER...
> UPLOADING FILE TO NEURAL NETWORK...`;
    
    // Determine endpoint based on conversion type
    const endpoints = {
      1: '/convert/excel-to-json',
      2: '/convert/json-to-excel', 
      3: '/convert/excel-to-sql',
      4: '/convert/formats'
    };
    
    const endpoint = endpoints[option] || endpoints[1];
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // Handle different response types
    if (option === 2) {
      // JSON to Excel - Check if response includes temp_file_path
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        // New response format with temp_file_path
        const result = await response.json();
        
        if (result.temp_file_path) {
          // Instead of trying to download from server, we'll create a download URL
          // The backend should provide a download endpoint or return the file directly
          try {
            // Try to get the file content using the temp_file_path as reference
            const fileResponse = await fetch(`${API_BASE_URL}/download-file`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ file_path: result.temp_file_path })
            });
            
            if (fileResponse.ok) {
              const blob = await fileResponse.blob();
              result.isFileDownload = true;
              result.blob = blob;
              return result;
            } else {
              console.warn('Could not download from temp path, falling back to original response');
              // If download fails, treat as successful conversion but without blob
              result.isFileDownload = true;
              // Create a placeholder blob or handle differently
              result.blob = new Blob(['File was generated successfully but download path is not available'], 
                                   { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
              return result;
            }
          } catch (downloadError) {
            console.warn('Download error:', downloadError);
            // Fallback: treat as successful but with limited download capability
            result.isFileDownload = true;
            result.downloadError = true;
            return result;
          }
        }
        
        return result;
      } else {
        // Legacy blob response format
        const blob = await response.blob();
        const result = {
          status: 'SUCCESS',
          isFileDownload: true,
          blob: blob,
          filename: 'converted_data.xlsx',
          metadata: {
            processing_time: 'N/A',
            ai_usage: {
              user_friendly_explanation: '✅ Archivo Excel generado exitosamente.'
            }
          }
        };
        return result;
      }
    } else {
      // Other conversions return JSON
      const result = await response.json();
      result.isFileDownload = false;
      return result;
    }
    
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

const processFile = async () => {
  if (!selectedOption.value) {
    displayedText.value += `\n> ERROR: NO PROTOCOL SELECTED
> PLEASE SELECT A CONVERSION PROTOCOL FIRST`;
    return;
  }
  
  // Only require file for options 1, 2, and 3 (not for option 4 - formats)
  if (!selectedFile.value && selectedOption.value !== 4) {
    displayedText.value += `\n> ERROR: NO FILE LOADED
> PLEASE SELECT A FILE FIRST`;
    return;
  }
  
  isProcessing.value = true;
  
  try {
    displayedText.value += `\n> EXECUTING PROTOCOL [${selectedOption.value}]...
> INITIALIZING AI ANALYSIS ENGINE...
> PROCESSING DATA WITH NEURAL NETWORK...`;
    
    // Simulate processing steps
    const steps = [
      '> PARSING EXCEL STRUCTURE...',
      '> ANALYZING COLUMN HEADERS...',
      '> DETECTING DATA TYPES...',
      '> INFERRING RELATIONSHIPS...',
      '> GENERATING JSON SCHEMA...',
      '> CONVERTING TO JSON FORMAT...'
    ];
    
    for (let i = 0; i < steps.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      displayedText.value += `\n${steps[i]}`;
    }
    
    // Call backend API
    const result = await callBackendAPI(selectedFile.value, selectedOption.value);
    
    conversionResult.value = result;
    
    if (selectedOption.value === 4) {
      // Handle formats response
      displayedText.value += `\n> FORMATS ANALYSIS COMPLETED!
> SUPPORTED FORMATS: ${result.supported_formats?.length || 'Multiple'}
> INPUT TYPES: ${result.input_formats?.join(', ') || 'Excel, JSON, CSV'}
> OUTPUT TYPES: ${result.output_formats?.join(', ') || 'JSON, Excel, SQL'}
> AI FEATURES: ${result.ai_features ? 'ENABLED' : 'BASIC MODE'}
> STATUS: ANALYSIS COMPLETE
> MISSION CONTROL: ACTIVATED`;
    } else if (result.isFileDownload || result.temp_file_path) {
      // Handle file download response (JSON → Excel)
      displayedText.value += `\n> EXCEL FILE GENERATED SUCCESSFULLY!
> FILENAME: ${result.filename || 'converted_data.xlsx'}
> STATUS: READY FOR DOWNLOAD
> AI PROCESSING: ${result.metadata?.ai_usage?.processing_mode?.toUpperCase() || 'DETERMINISTIC'}
> CONFIDENCE: ${result.metadata?.confidence || result.metadata?.ai_analysis?.confidence || '95'}%
> MISSION CONTROL: ACTIVATED`;
    } else {
      // Handle JSON response (Excel → JSON, etc.)
      displayedText.value += `\n> CONVERSION COMPLETED SUCCESSFULLY!
> AI CONFIDENCE: ${result.metadata?.confidence || result.metadata?.ai_analysis?.confidence || '95'}%
> PROCESSING MODE: ${result.metadata?.ai_usage?.processing_mode?.toUpperCase() || 'DETERMINISTIC'}
> RECORDS PROCESSED: ${result.metadata?.record_count || 'Unknown'}
> OUTPUT FORMAT: ${getOutputFormat(selectedOption.value)}
> STATUS: READY FOR DOWNLOAD
> MISSION CONTROL: ACTIVATED`;
    }
    
    // Show mission control after a short delay
    setTimeout(() => {
      showMissionControl.value = true;
    }, 2000);
    
  } catch (error) {
    displayedText.value += `\n> ERROR: CONVERSION FAILED
> REASON: ${error.message}
> STATUS: CONNECTION TO AI SERVER LOST
> PLEASE TRY AGAIN OR CONTACT SUPPORT`;
  } finally {
    isProcessing.value = false;
  }
};

// Get output format based on input
const getOutputFormat = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  // For JSON files → convert to Excel
  if (extension === 'json') {
    return 'xlsx';
  }
  
  // For Excel files (xlsx, xls), CSV → convert to JSON
  if (['xlsx', 'xls', 'csv'].includes(extension)) {
    return 'json';
  }
  
  // Default to JSON for unknown formats
  return 'json';
};

// Get conversion endpoint based on file type
const getConversionEndpoint = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase();
  
  // For JSON files → use json-to-excel endpoint
  if (extension === 'json') {
    return 'json-to-excel';
  }
  
  // For Excel and CSV files → use default convert endpoint
  return 'convert';
};

// Download result based on conversion type
const downloadResult = () => {
  if (!conversionResult.value) return;
  
  if (conversionResult.value.isFileDownload || conversionResult.value.temp_file_path) {
    // Check if we have a blob to download
    if (conversionResult.value.blob && !conversionResult.value.downloadError) {
      // Download Excel file (JSON → Excel)
      const blob = conversionResult.value.blob;
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = conversionResult.value.filename || 'converted_data.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      displayedText.value += `\n> EXCEL FILE DOWNLOADED: ${link.download}
> AI PROCESSING: ${conversionResult.value.metadata?.ai_usage?.processing_mode?.toUpperCase() || 'DETERMINISTIC'}
> STATUS: CONVERSION COMPLETE`;
    } else {
      // Handle case where file was generated but download is not available
      displayedText.value += `\n> FILE GENERATED: ${conversionResult.value.filename || 'converted_data.xlsx'}
> LOCATION: ${conversionResult.value.temp_file_path || 'Server location'}
> AI PROCESSING: ${conversionResult.value.metadata?.ai_usage?.processing_mode?.toUpperCase() || 'DETERMINISTIC'}
> STATUS: FILE READY (Check server location for download)`;
      
      // Show an alert to the user
      alert(`File generated successfully: ${conversionResult.value.filename || 'converted_data.xlsx'}\n\nFile location: ${conversionResult.value.temp_file_path || 'Server location'}\n\nNote: Automatic download not available. Please check the server location.`);
    }
  } else {
    // Download JSON file (Excel → JSON, etc.)
    const jsonString = JSON.stringify(conversionResult.value.data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `converted_${selectedFile.value.name.replace(/\.[^/.]+$/, '')}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    displayedText.value += `\n> JSON FILE DOWNLOADED: ${link.download}
> AI PROCESSING: ${conversionResult.value.metadata?.ai_usage?.processing_mode?.toUpperCase() || 'DETERMINISTIC'}
> STATUS: CONVERSION COMPLETE`;
  }
};

// Toggle preview
const togglePreview = () => {
  showPreview.value = !showPreview.value;
};

// Toggle technical details
const toggleDetails = () => {
  showDetails.value = !showDetails.value;
};

// Format JSON for preview (limit size)
const formatJsonPreview = (data) => {
  if (!data) return '';
  
  // If array, show first 3 items
  if (Array.isArray(data)) {
    const preview = data.slice(0, 3);
    const result = JSON.stringify(preview, null, 2);
    return data.length > 3 ? result + '\n\n... and ' + (data.length - 3) + ' more items' : result;
  }
  
  return JSON.stringify(data, null, 2);
};

// Helper functions for UI
const getModeClass = (mode) => {
  if (!mode) return 'mode-default';
  
  const classes = {
    'deterministic': 'mode-deterministic',
    'ai_powered': 'mode-ai',
    'fallback_optimization': 'mode-fallback',
    'hybrid': 'mode-hybrid'
  };
  return classes[mode] || 'mode-default';
};

const getModeIcon = (aiUsed) => {
  return aiUsed ? '🤖' : '⚙️';
};

const getModeText = (mode) => {
  if (!mode) return 'STANDARD PROCESSING';
  
  const texts = {
    'deterministic': 'DETERMINISTIC ENGINE',
    'ai_powered': 'AI NEURAL NETWORK',
    'fallback_optimization': 'OPTIMIZED PROCESSING',
    'hybrid': 'HYBRID AI + DETERMINISTIC'
  };
  return texts[mode] || mode.toString().toUpperCase();
};

const getConfidenceClass = (confidence) => {
  if (confidence == null || confidence === undefined) return 'confidence-low';
  if (confidence >= 90) return 'confidence-excellent';
  if (confidence >= 80) return 'confidence-good';
  if (confidence >= 70) return 'confidence-ok';
  return 'confidence-low';
};

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 KB';
  
  const kb = bytes / 1024;
  const mb = kb / 1024;
  
  if (mb >= 1) return `${mb.toFixed(2)} MB`;
  return `${kb.toFixed(2)} KB`;
};

const formatIssue = (issue) => {
  if (!issue) return '';
  // Format technical issues to be more user-friendly
  return issue.replace(/_/g, ' ').replace(/high_missing_data_in_columns_/, 'Missing data in columns: ');
};

const getTypeClass = (type) => {
  if (!type) return 'type-default';
  
  const classes = {
    'numeric': 'type-numeric',
    'text': 'type-text',
    'datetime': 'type-datetime',
    'email': 'type-email',
    'boolean': 'type-boolean'
  };
  return classes[type] || 'type-default';
};

// Mission Control Functions
const startNewMission = () => {
  // Reset for new file with same protocol
  selectedFile.value = null;
  conversionResult.value = null;
  showPreview.value = false;
  showDetails.value = false;
  showMissionControl.value = false;
  showUpload.value = true;
  
  displayedText.value += `\n\n> NEW MISSION INITIATED
> PROTOCOL [${selectedOption.value}] REMAINS ACTIVE
> AWAITING NEW FILE INPUT...`;
  
  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const changeProtocol = () => {
  // Full reset to protocol selection
  selectedFile.value = null;
  conversionResult.value = null;
  showPreview.value = false;
  showDetails.value = false;
  showMissionControl.value = false;
  showUpload.value = false;
  showOptions.value = true;
  selectedOption.value = null;
  
  displayedText.value += `\n\n> PROTOCOL CHANGE REQUESTED
> RETURNING TO MISSION SELECTION
> NEURAL NETWORK READY FOR NEW PROTOCOL...`;
  
  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const downloadAndExit = () => {
  // Download the file and show exit message
  downloadResult();
  
  const fileType = conversionResult.value?.isFileDownload ? 'EXCEL' : 'JSON';
  
  displayedText.value += `\n\n> ${fileType} DOWNLOAD INITIATED
> MISSION COMPLETE - DATA SUCCESSFULLY CONVERTED
> DISCONNECTING FROM MATRIX...
> CONNECTION TERMINATED`;
  
  // Hide mission control and show a final message
  showMissionControl.value = false;
  
  setTimeout(() => {
    displayedText.value += `\n\n> THANK YOU FOR USING MATRIX AI CONVERTER
> ${fileType} CONVERSION PROTOCOL COMPLETED
> NEURAL NETWORK SHUTTING DOWN...
> GOODBYE, AGENT 🔋`;
  }, 1500);
};
</script>

<style scoped>
/* Matrix background */
.matrix-bg {
  background: #000;
  position: relative;
}

/* Terminal container */
.terminal-container {
  width: 800px;
  background: rgba(0, 0, 0, 0.9);
  border: 2px solid #00ff00;
  border-radius: 10px;
  box-shadow: 
    0 0 20px #00ff00,
    inset 0 0 20px rgba(0, 255, 0, 0.1);
  overflow: hidden;
}

/* Terminal header */
.terminal-header {
  background: linear-gradient(90deg, #001100, #003300);
  padding: 10px 20px;
  border-bottom: 1px solid #00ff00;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.terminal-buttons {
  display: flex;
  gap: 8px;
}

.terminal-button {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: block;
}

.terminal-button.red { background: #ff5f56; }
.terminal-button.yellow { background: #ffbd2e; }
.terminal-button.green { background: #27ca3f; }

.terminal-title {
  color: #00ff00;
  font-weight: bold;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* Terminal content */
.terminal-content {
  padding: 30px;
  min-height: 500px;
}

/* Matrix logo with glitch effect */
.matrix-logo {
  font-size: 24px;
  color: #00ff00;
  text-align: center;
  font-weight: bold;
  text-shadow: 0 0 10px #00ff00;
  letter-spacing: 3px;
}

.glitch {
  position: relative;
  animation: glitch 2s infinite;
}

.glitch::before,
.glitch::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.glitch::before {
  animation: glitch-1 0.5s infinite;
  color: #ff0000;
  z-index: -1;
}

.glitch::after {
  animation: glitch-2 0.5s infinite;
  color: #0000ff;
  z-index: -2;
}

/* Terminal text */
.terminal-text {
  color: #00ff00;
  line-height: 1.6;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.typing-text {
  white-space: pre-line;
}

.cursor {
  color: #00ff00;
  animation: blink 1s infinite;
}

/* Options Menu */
.options-container {
  text-align: center;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.option-button {
  background: rgba(0, 20, 0, 0.8);
  border: 2px solid #004400;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  color: #00cc00;
  font-family: 'Courier New', monospace;
}

.option-button:hover {
  border-color: #00ff00;
  background: rgba(0, 40, 0, 0.9);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
  transform: translateY(-2px);
}

.option-button.selected {
  border-color: #00ff00;
  background: rgba(0, 60, 0, 0.9);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
}

.option-number {
  font-size: 18px;
  font-weight: bold;
  color: #00ff00;
  margin-bottom: 5px;
}

.option-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #00dd00;
}

.option-description {
  font-size: 12px;
  color: #009900;
  line-height: 1.4;
}

.options-hint {
  color: #00aa00;
  font-size: 12px;
  margin-top: 10px;
}

.blink {
  animation: blink 1s infinite;
}

/* Upload container */
.upload-container {
  text-align: center;
}

.upload-border {
  border: 2px dashed #00ff00;
  border-radius: 8px;
  padding: 20px;
  background: rgba(0, 255, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.upload-border:hover {
  background: rgba(0, 255, 0, 0.1);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
}

.upload-inner {
  position: relative;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-text {
  color: #00ff00;
  font-size: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-icon {
  font-size: 30px;
}

/* Upload button */
.upload-button {
  background: linear-gradient(45deg, #001100, #003300);
  border: 2px solid #00ff00;
  color: #00ff00;
  padding: 12px 30px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.upload-button:hover {
  background: linear-gradient(45deg, #003300, #005500);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
  transform: translateY(-2px);
}

.button-text {
  position: relative;
}

/* System info */
.system-info {
  position: fixed;
  bottom: 20px;
  right: 20px;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  text-align: right;
  line-height: 1.4;
  opacity: 0.7;
  z-index: 10;
}

/* Scanlines effect */
.scanlines {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    transparent 0%,
    transparent 48%,
    rgba(0, 255, 0, 0.02) 49%,
    rgba(0, 255, 0, 0.02) 50%,
    transparent 51%,
    transparent 100%
  );
  background-size: 100% 4px;
  pointer-events: none;
  z-index: 1000;
}

/* Matrix rain effect */
.matrix-rain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.1;
  z-index: 1;
}

.matrix-rain::before {
  content: "10101010011010101101010100110101011010101001101010110101010011010101101010100110101011010101001101010110101010011010101101010100110101011010101001101010110101010011010101101010100110101011010101001101010110101010011010101101010100110101011010101001101010110101010011010101101010100110101011010101001101010110101010011010101";
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 200%;
  color: #00ff00;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 14px;
  word-break: break-all;
  animation: matrix-fall 20s linear infinite;
}

/* Animations */
@keyframes glitch {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
}

@keyframes glitch-1 {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(-1px, 1px); }
  40% { transform: translate(-1px, -1px); }
  60% { transform: translate(1px, 1px); }
  80% { transform: translate(1px, -1px); }
}

@keyframes glitch-2 {
  0%, 100% { transform: translate(0); }
  20% { transform: translate(1px, -1px); }
  40% { transform: translate(1px, 1px); }
  60% { transform: translate(-1px, -1px); }
  80% { transform: translate(-1px, 1px); }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes matrix-fall {
  from { transform: translateY(-100%); }
  to { transform: translateY(100vh); }
}

/* Results Container */
.results-container {
  border: 2px solid #00ff00;
  border-radius: 8px;
  background: rgba(0, 20, 0, 0.8);
  overflow: hidden;
}

.results-header {
  background: linear-gradient(90deg, #001100, #003300);
  padding: 12px 20px;
  border-bottom: 1px solid #00ff00;
  text-align: center;
}

.results-title {
  color: #00ff00;
  font-weight: bold;
  font-size: 16px;
}

.results-content {
  padding: 20px;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px;
  border: 1px solid #004400;
  border-radius: 5px;
  background: rgba(0, 10, 0, 0.5);
}

.stat-label {
  display: block;
  color: #00aa00;
  font-size: 12px;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  color: #00ff00;
  font-weight: bold;
  font-size: 14px;
}

.stat-value.success {
  color: #00ff00;
  text-shadow: 0 0 5px #00ff00;
}

.result-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
}

.download-button, .preview-button {
  padding: 12px 24px;
  border: 2px solid #00aa00;
  border-radius: 5px;
  background: rgba(0, 30, 0, 0.8);
  color: #00ff00;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-button:hover, .preview-button:hover {
  border-color: #00ff00;
  background: rgba(0, 50, 0, 0.9);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
}

.upload-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-button.processing {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.preview-area {
  border: 1px solid #004400;
  border-radius: 5px;
  background: rgba(0, 5, 0, 0.7);
  overflow: hidden;
}

.preview-header {
  background: rgba(0, 20, 0, 0.8);
  padding: 8px 15px;
  color: #00aa00;
  font-size: 12px;
  border-bottom: 1px solid #004400;
}

.json-preview {
  padding: 15px;
  color: #00cc00;
  font-size: 11px;
  line-height: 1.4;
  max-height: 200px;
  overflow-y: auto;
  margin: 0;
  white-space: pre-wrap;
}

/* Enhanced Results Styles */
.processing-mode-info {
  text-align: center;
  border-bottom: 1px solid #004400;
  padding-bottom: 15px;
}

.mode-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 10px;
}

.mode-deterministic {
  background: rgba(0, 100, 0, 0.3);
  border: 1px solid #006600;
  color: #00dd00;
}

.mode-ai {
  background: rgba(0, 0, 100, 0.3);
  border: 1px solid #0066ff;
  color: #66aaff;
}

.mode-fallback {
  background: rgba(100, 100, 0, 0.3);
  border: 1px solid #666600;
  color: #dddd00;
}

.mode-hybrid {
  background: rgba(50, 0, 100, 0.3);
  border: 1px solid #6600cc;
  color: #cc66ff;
}

.user-explanation {
  color: #00aa00;
  font-size: 13px;
  line-height: 1.4;
  font-style: italic;
}

.confidence-excellent { color: #00ff00; text-shadow: 0 0 5px #00ff00; }
.confidence-good { color: #88ff00; }
.confidence-ok { color: #ffff00; }
.confidence-low { color: #ff8800; }

.file-info-section, .ai-analysis-section {
  border: 1px solid #003300;
  border-radius: 5px;
  padding: 15px;
  background: rgba(0, 10, 0, 0.5);
}

.section-title {
  color: #00ff00;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 10px;
  text-align: center;
}

.file-details {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #002200;
}

.detail-label {
  color: #00aa00;
  font-size: 12px;
  font-weight: bold;
}

.detail-value {
  color: #00dd00;
  font-size: 12px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.analysis-label {
  color: #00aa00;
  font-size: 12px;
  font-weight: bold;
}

.analysis-value {
  color: #00dd00;
  font-size: 12px;
}

.issues-section, .recommendations-section {
  margin-top: 15px;
  padding: 10px;
  border-left: 3px solid #ff6600;
  background: rgba(40, 20, 0, 0.3);
}

.issues-title, .recommendations-title {
  color: #ff8800;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 8px;
}

.issues-list, .recommendations-list {
  margin: 0;
  padding-left: 15px;
  color: #ffaa00;
  font-size: 11px;
  line-height: 1.4;
}

/* AI Usage Details */
.ai-usage-details {
  border: 1px solid #004400;
  border-radius: 5px;
  padding: 15px;
  background: rgba(0, 15, 0, 0.6);
}

.ai-usage-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.usage-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid #002200;
}

.usage-label {
  color: #00bb00;
  font-size: 12px;
  font-weight: bold;
}

.usage-value {
  color: #00ff00;
  font-size: 12px;
  font-weight: bold;
}

.usage-value.ai-active {
  color: #00ff00;
  text-shadow: 0 0 3px #00ff00;
}

.usage-value.ai-inactive {
  color: #888888;
}

.usage-value.mode-value {
  color: #00dddd;
  text-shadow: 0 0 2px #00dddd;
}

.ai-improvements {
  margin-top: 15px;
  padding: 10px;
  border-left: 3px solid #00ff00;
  background: rgba(0, 40, 0, 0.3);
}

.improvements-title {
  color: #00ff00;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 8px;
}

.improvements-list {
  margin: 0;
  padding-left: 15px;
  color: #88ff88;
  font-size: 11px;
  line-height: 1.4;
}

.technical-details-ai {
  margin-top: 15px;
  padding: 10px;
  border-left: 3px solid #666666;
  background: rgba(20, 20, 20, 0.3);
}

.technical-title {
  color: #cccccc;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 8px;
}

.technical-content {
  color: #aaaaaa;
  font-size: 10px;
  font-family: 'Courier New', monospace;
  line-height: 1.3;
  margin: 0;
  white-space: pre-wrap;
}

.details-button {
  padding: 12px 24px;
  border: 2px solid #0066aa;
  border-radius: 5px;
  background: rgba(0, 20, 40, 0.8);
  color: #6699ff;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.details-button:hover {
  border-color: #0099ff;
  background: rgba(0, 30, 60, 0.9);
  box-shadow: 0 0 15px rgba(0, 150, 255, 0.3);
}

.technical-details {
  border: 1px solid #004466;
  border-radius: 5px;
  background: rgba(0, 10, 20, 0.8);
  padding: 15px;
}

.details-header {
  color: #66aaff;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 15px;
  text-align: center;
  border-bottom: 1px solid #003366;
  padding-bottom: 8px;
}

.detail-section-title {
  color: #4488ff;
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 10px;
}

.column-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.column-type-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  border: 1px solid #002244;
  border-radius: 4px;
  background: rgba(0, 5, 15, 0.5);
}

.column-name {
  color: #88aaff;
  font-size: 11px;
  font-weight: bold;
}

.column-type {
  font-size: 10px;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 3px;
}

.type-numeric { background: #003300; color: #00ff00; }
.type-text { background: #330000; color: #ff6666; }
.type-datetime { background: #000033; color: #6666ff; }
.type-email { background: #330033; color: #ff66ff; }
.type-boolean { background: #333300; color: #ffff66; }
.type-default { background: #222222; color: #aaaaaa; }

/* Mission Control Styles */
.mission-control-container {
  border: 2px solid #00ff00;
  border-radius: 10px;
  background: rgba(0, 30, 0, 0.9);
  overflow: hidden;
  animation: mission-appear 1s ease-out;
  box-shadow: 
    0 0 30px rgba(0, 255, 0, 0.4),
    inset 0 0 30px rgba(0, 255, 0, 0.1);
}

@keyframes mission-appear {
  from { 
    opacity: 0; 
    transform: translateY(20px) scale(0.95);
  }
  to { 
    opacity: 1; 
    transform: translateY(0) scale(1);
  }
}

.mission-header {
  background: linear-gradient(135deg, #001100, #003300, #001100);
  padding: 20px;
  text-align: center;
  border-bottom: 2px solid #00ff00;
  position: relative;
}

.mission-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ff00, transparent);
  animation: mission-scan 3s ease-in-out infinite;
}

@keyframes mission-scan {
  0%, 100% { transform: translateX(-100%); }
  50% { transform: translateX(100%); }
}

.mission-title {
  color: #00ff00;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 0 0 10px #00ff00;
  animation: mission-glow 2s ease-in-out infinite alternate;
}

@keyframes mission-glow {
  from { text-shadow: 0 0 10px #00ff00; }
  to { text-shadow: 0 0 20px #00ff00, 0 0 30px #00ff00; }
}

.mission-subtitle {
  color: #88ff88;
  font-size: 14px;
  margin-bottom: 5px;
}

.mission-status {
  color: #66dd66;
  font-size: 12px;
  animation: blink 1.5s infinite;
}

.mission-content {
  padding: 25px;
}

.mission-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 25px;
  padding: 15px;
  background: rgba(0, 20, 0, 0.6);
  border-radius: 8px;
  border: 1px solid #004400;
}

.mission-stat {
  text-align: center;
  flex: 1;
}

.stat-icon {
  display: block;
  font-size: 18px;
  margin-bottom: 5px;
}

.stat-text {
  color: #00dd00;
  font-size: 11px;
  font-weight: bold;
}

.mission-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.mission-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Courier New', monospace;
  font-weight: bold;
  position: relative;
  overflow: hidden;
}

.mission-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s;
}

.mission-button:hover::before {
  left: 100%;
}

.mission-button.primary {
  background: rgba(0, 60, 0, 0.8);
  border: 2px solid #00aa00;
  color: #00ff00;
}

.mission-button.primary:hover {
  background: rgba(0, 80, 0, 0.9);
  border-color: #00ff00;
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.4);
  transform: translateY(-3px);
}

.mission-button.secondary {
  background: rgba(0, 0, 60, 0.8);
  border: 2px solid #0066aa;
  color: #66aaff;
}

.mission-button.secondary:hover {
  background: rgba(0, 0, 80, 0.9);
  border-color: #0099ff;
  box-shadow: 0 0 20px rgba(0, 150, 255, 0.4);
  transform: translateY(-3px);
}

.mission-button.accent {
  background: rgba(60, 0, 60, 0.8);
  border: 2px solid #aa0066;
  color: #ff66aa;
}

.mission-button.accent:hover {
  background: rgba(80, 0, 80, 0.9);
  border-color: #ff0099;
  box-shadow: 0 0 20px rgba(255, 0, 150, 0.4);
  transform: translateY(-3px);
}

.button-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.button-label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 5px;
}

.button-desc {
  font-size: 10px;
  opacity: 0.8;
  text-align: center;
}

.mission-footer {
  text-align: center;
  padding-top: 15px;
  border-top: 1px solid #004400;
}

.matrix-signature {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #008800;
  font-size: 11px;
}

.signature-status {
  color: #00ff00;
  animation: blink 2s infinite;
}

/* Global styles */
body {
  font-family: 'Courier New', monospace;
  overflow: hidden;
}
</style>
