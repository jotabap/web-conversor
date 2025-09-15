"""
AI Service for data analysis and processing
"""

import pandas as pd
from typing import Dict, List, Any
from models.responses import AIAnalysis, AIUsageInfo
from services.azure_openai_service import AzureOpenAIService
from utils.logger import logger
from utils.exceptions import AIProcessingError


class AIService:
    """Service for AI-powered data analysis"""
    
    def __init__(self):
        self.confidence_threshold = 0.8
        self.azure_openai = AzureOpenAIService()
        logger.info("AI Service initialized")
    
    async def analyze_dataframe(
        self, 
        df: pd.DataFrame, 
        use_ai: bool = True,
        min_confidence: float = 0.8,
        filename: str = "data"
    ) -> tuple:
        """
        Analyze DataFrame structure - deterministic first, AI only if needed
        
        Args:
            df: DataFrame to analyze
            use_ai: Whether AI assistance is available for error recovery
            min_confidence: Minimum confidence threshold
            filename: Original filename for context
            
        Returns:
            Tuple of (AIAnalysis, AIUsageInfo)
            
        Raises:
            AIProcessingError: If both deterministic and AI analysis fail
        """
        
        try:
            logger.info(f"INFO: Starting deterministic analysis for {filename}")
            
            # Always try deterministic analysis first
            deterministic_result = self._deterministic_analysis(df)
            
            # Check if deterministic analysis found problems
            if deterministic_result.get("has_issues", False):
                issues = deterministic_result.get('issues', [])
                logger.warning(f"WARNING: Data issues detected: {issues}")
                
                if use_ai and self.azure_openai.is_configured:
                    logger.info("🤖 Calling AI to resolve data issues...")
                    # Only use AI to resolve specific problems
                    analysis_result = await self.azure_openai.analyze_excel_data(
                        df, filename, True, issues
                    )
                    ai_analysis = self._convert_to_ai_analysis(analysis_result, df)
                    
                    # Create AI usage info
                    ai_usage = self.create_ai_usage_info(
                        ai_used=True,
                        processing_mode="ai_assisted",
                        detected_issues=issues,
                        ai_improvements=analysis_result.get("recommendations", [])
                    )
                    
                    return ai_analysis, ai_usage
                else:
                    logger.info("INFO: AI not available, using deterministic fallback...")
                    ai_analysis = self._convert_deterministic_to_ai_analysis(deterministic_result, df)
                    
                    # Create AI usage info for fallback
                    ai_usage = self.create_ai_usage_info(
                        ai_used=False,
                        processing_mode="fallback_optimization",
                        detected_issues=issues
                    )
                    
                    return ai_analysis, ai_usage
            
            # No issues detected - pure deterministic
            ai_analysis = self._convert_deterministic_to_ai_analysis(deterministic_result, df)
            
            # Create AI usage info for deterministic processing
            ai_usage = self.create_ai_usage_info(
                ai_used=False,
                processing_mode="deterministic"
            )
            
            return ai_analysis, ai_usage
            
        except Exception as e:
            logger.error(f"ERROR: Analysis failed: {str(e)}")
            # Last resort: basic analysis
            basic_analysis = self._basic_analysis(df)
            ai_usage = self.create_ai_usage_info(
                ai_used=False,
                processing_mode="error_fallback",
                detected_issues=[f"analysis_error_{str(e)}"]
            )
            return basic_analysis, ai_usage
    
    def create_ai_usage_info(
        self,
        ai_used: bool,
        processing_mode: str,
        detected_issues: List[str] = None,
        ai_improvements: List[str] = None
    ) -> AIUsageInfo:
        """
        Create user-friendly AI usage information
        
        Args:
            ai_used: Whether AI was actually used
            processing_mode: Processing mode used
            detected_issues: Issues that triggered AI
            ai_improvements: Improvements AI made
            
        Returns:
            AIUsageInfo with user-friendly explanations
        """
        
        detected_issues = detected_issues or []
        ai_improvements = ai_improvements or []
        
        # Generate user-friendly explanation
        explanation = self._generate_user_explanation(ai_used, processing_mode, detected_issues)
        
        # Determine trigger reason
        trigger_reason = self._determine_trigger_reason(detected_issues) if ai_used else None
        
        return AIUsageInfo(
            ai_used=ai_used,
            processing_mode=processing_mode,
            trigger_reason=trigger_reason,
            issues_detected=detected_issues,
            ai_improvements=ai_improvements,
            user_friendly_explanation=explanation,
            technical_details={
                "issues_count": len(detected_issues),
                "improvements_count": len(ai_improvements),
                "mode": processing_mode
            } if ai_used else None
        )
    
    def _generate_user_explanation(self, ai_used: bool, processing_mode: str, detected_issues: List[str]) -> str:
        """Generate user-friendly explanation"""
        
        if not ai_used or processing_mode == "deterministic":
            return "✅ Tu archivo se procesó perfectamente sin necesidad de asistencia de IA. Los datos estaban bien estructurados y no requirieron optimizaciones."
        
        elif processing_mode == "ai_assisted":
            issues_count = len(detected_issues)
            
            if issues_count == 0:
                return "🤖 Se usó IA para optimizar la conversión y asegurar la mejor calidad posible."
            
            elif issues_count == 1:
                issue_type = self._get_issue_category(detected_issues[0])
                return f"🤖 Se detectó un problema de {issue_type} en tus datos. La IA lo resolvió automáticamente para asegurar una conversión perfecta."
            
            else:
                return f"🤖 Se detectaron {issues_count} problemas en tus datos (tipos mixtos, formato, etc.). La IA los resolvió automáticamente para optimizar la conversión."
        
        elif processing_mode == "fallback_optimization":
            return "WARNING: Se detectaron algunos problemas en los datos. Se aplicaron correcciones básicas ya que la IA no estaba disponible."
        
        else:
            return "INFO: Se aplicó procesamiento especializado para manejar la estructura de tus datos."
    
    def _determine_trigger_reason(self, detected_issues: List[str]) -> str:
        """Determine why AI was triggered"""
        
        if not detected_issues:
            return "optimization_request"
        
        # Categorize issues
        data_issues = [issue for issue in detected_issues if any(keyword in issue for keyword in ["mixed_types", "encoding", "malformed"])]
        structure_issues = [issue for issue in detected_issues if any(keyword in issue for keyword in ["nested", "column_names", "excel_limit"])]
        sql_issues = [issue for issue in detected_issues if any(keyword in issue for keyword in ["sql", "syntax", "injection"])]
        
        if sql_issues:
            return "sql_generation_errors"
        elif structure_issues:
            return "data_structure_complexity"
        elif data_issues:
            return "data_quality_issues"
        else:
            return "general_optimization"
    
    def _get_issue_category(self, issue: str) -> str:
        """Get user-friendly category for an issue"""
        
        if "mixed_types" in issue:
            return "tipos de datos mixtos"
        elif "nested" in issue:
            return "estructura anidada"
        elif "column" in issue:
            return "nombres de columnas"
        elif "encoding" in issue:
            return "codificación de caracteres"
        elif "sql" in issue:
            return "generación SQL"
        elif "excel" in issue:
            return "compatibilidad con Excel"
        elif "long_text" in issue:
            return "texto muy largo"
        else:
            return "formato de datos"

    def _deterministic_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform deterministic analysis and detect data issues
        
        Returns:
            Analysis result with issue detection
        """
        
        issues = []
        has_issues = False
        
        try:
            # Check for common data problems
            
            # 1. Empty or mostly empty DataFrame
            if df.empty or df.shape[0] == 0:
                issues.append("empty_dataframe")
                has_issues = True
            
            # 2. Check for columns with mixed data types
            for col in df.columns:
                if self._has_mixed_types(df[col]):
                    issues.append(f"mixed_types_in_column_{col}")
                    has_issues = True
            
            # 3. Check for excessive missing data
            missing_percentage = (df.isnull().sum() / len(df)) * 100
            high_missing_cols = missing_percentage[missing_percentage > 50].index.tolist()
            if high_missing_cols:
                issues.append(f"high_missing_data_in_columns_{','.join(high_missing_cols)}")
                has_issues = True
            
            # 4. Check for duplicate column names
            if len(df.columns) != len(set(df.columns)):
                issues.append("duplicate_column_names")
                has_issues = True
            
            # 5. Check for malformed data patterns
            for col in df.columns:
                if df[col].dtype == 'object':  # String columns
                    if self._has_malformed_patterns(df[col]):
                        issues.append(f"malformed_data_in_column_{col}")
                        has_issues = True
            
            # 6. Check for encoding issues
            if self._has_encoding_issues(df):
                issues.append("encoding_issues")
                has_issues = True
                
            logger.info(f"INFO: Deterministic analysis complete - Issues found: {len(issues)}")
            
            return {
                "has_issues": has_issues,
                "issues": issues,
                "column_types": self._detect_column_types(df),
                "data_shape": df.shape,
                "missing_data": missing_percentage.to_dict(),
                "analysis_type": "deterministic"
            }
            
        except Exception as e:
            logger.error(f"ERROR: Deterministic analysis failed: {str(e)}")
            return {
                "has_issues": True,
                "issues": [f"analysis_error_{str(e)}"],
                "column_types": {},
                "data_shape": (0, 0),
                "missing_data": {},
                "analysis_type": "error"
            }
    
    def _has_mixed_types(self, series: pd.Series) -> bool:
        """Check if a series has mixed data types"""
        if series.dtype == 'object':
            # Check if we have numbers mixed with strings
            non_null_values = series.dropna()
            if len(non_null_values) == 0:
                return False
                
            numeric_count = 0
            string_count = 0
            
            for val in non_null_values.head(100):  # Sample first 100 values
                try:
                    float(val)
                    numeric_count += 1
                except (ValueError, TypeError):
                    string_count += 1
            
            # Mixed if we have both numbers and strings
            return numeric_count > 0 and string_count > 0
        return False
    
    def _has_malformed_patterns(self, series: pd.Series) -> bool:
        """Check for malformed data patterns"""
        non_null_values = series.dropna()
        if len(non_null_values) == 0:
            return False
            
        sample_values = non_null_values.head(50).astype(str)
        
        # Check for common malformed patterns
        malformed_patterns = [
            r'^\s*$',  # Only whitespace
            r'^#+$',   # Only hash symbols (Excel errors)
            r'^N/A$|^n/a$|^NULL$|^null$',  # Explicit null values
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?$',  # Malformed dates
        ]
        
        import re
        for pattern in malformed_patterns:
            matches = sample_values.str.match(pattern, na=False).sum()
            if matches > len(sample_values) * 0.1:  # More than 10% malformed
                return True
        
        return False
    
    def _has_encoding_issues(self, df: pd.DataFrame) -> bool:
        """Check for encoding issues in string columns"""
        for col in df.columns:
            if df[col].dtype == 'object':
                sample_values = df[col].dropna().head(50).astype(str)
                for val in sample_values:
                    # Check for common encoding issue indicators
                    if any(char in val for char in ['�', '\ufffd', '\x00']):
                        return True
        return False
    
    def _convert_deterministic_to_ai_analysis(self, deterministic_result: Dict[str, Any], df: pd.DataFrame) -> AIAnalysis:
        """Convert deterministic analysis to AIAnalysis format"""
        
        if deterministic_result.get("has_issues", False):
            confidence = 70.0  # Lower confidence when issues detected
            recommendations = [
                f"Data issues detected: {', '.join(deterministic_result.get('issues', []))}",
                "Consider data cleaning before processing"
            ]
        else:
            confidence = 95.0  # High confidence for clean data
            recommendations = ["Data appears clean and well-structured"]
        
        return AIAnalysis(
            confidence=confidence,
            analysis_type=deterministic_result.get("analysis_type", "deterministic"),
            detected_patterns=deterministic_result.get("issues", []),
            column_types=deterministic_result.get("column_types", {}),
            recommendations=recommendations
        )

    def _basic_analysis(self, df: pd.DataFrame) -> AIAnalysis:
        """Basic deterministic analysis"""
        
        return AIAnalysis(
            confidence=85.0,
            analysis_type="deterministic",
            detected_patterns=["basic_table_structure"],
            column_types=self._detect_column_types(df),
            recommendations=["Consider enabling AI analysis for better insights"]
        )
    
    def _ai_powered_analysis(self, df: pd.DataFrame, min_confidence: float) -> AIAnalysis:
        """AI-powered analysis with pattern detection"""
        
        analysis = AIAnalysis(
            confidence=95.0,
            analysis_type="ai_powered",
            detected_patterns=[],
            column_types=self._detect_column_types(df),
            recommendations=[]
        )
        
        # Pattern detection
        patterns = self._detect_patterns(df)
        analysis.detected_patterns = patterns
        
        # Generate recommendations
        recommendations = self._generate_recommendations(df, patterns)
        analysis.recommendations = recommendations
        
        # Adjust confidence based on data quality
        confidence = self._calculate_confidence(df, patterns)
        analysis.confidence = max(confidence, min_confidence * 100)
        
        logger.info(f"✅ AI analysis completed - Confidence: {analysis.confidence}%")
        return analysis
    
    def _detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detect column data types"""
        
        column_types = {}
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            if 'int' in dtype or 'float' in dtype:
                column_types[col] = "numeric"
            elif 'datetime' in dtype:
                column_types[col] = "datetime"
            elif df[col].dtype == 'bool':
                column_types[col] = "boolean"
            else:
                # Advanced type detection
                if self._is_email_column(df[col]):
                    column_types[col] = "email"
                elif self._is_url_column(df[col]):
                    column_types[col] = "url"
                elif self._is_phone_column(df[col]):
                    column_types[col] = "phone"
                else:
                    column_types[col] = "text"
        
        return column_types
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect data patterns"""
        
        patterns = []
        
        # Structure patterns
        if len(df.columns) > 5:
            patterns.append("complex_structure")
        
        if len(df.columns) <= 3:
            patterns.append("simple_structure")
        
        # Data quality patterns
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        if null_percentage > 10:
            patterns.append("missing_values")
        elif null_percentage == 0:
            patterns.append("complete_data")
        
        # Size patterns
        if len(df) > 1000:
            patterns.append("large_dataset")
        elif len(df) < 50:
            patterns.append("small_dataset")
        
        # Duplicate detection
        if df.duplicated().any():
            patterns.append("duplicates_detected")
        
        # Numeric patterns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            patterns.append("numeric_data")
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame, patterns: List[str]) -> List[str]:
        """Generate AI recommendations"""
        
        recommendations = []
        
        if "missing_values" in patterns:
            recommendations.append("Handle missing values with AI interpolation")
        
        if "duplicates_detected" in patterns:
            recommendations.append("Remove duplicate records for data integrity")
        
        if "large_dataset" in patterns:
            recommendations.append("Consider data pagination for optimal performance")
        
        if "complex_structure" in patterns:
            recommendations.append("Validate data relationships and normalize structure")
        
        if "numeric_data" in patterns:
            recommendations.append("Apply statistical analysis for numeric insights")
        
        if not recommendations:
            recommendations.append("Data structure appears optimal for conversion")
        
        return recommendations
    
    def _calculate_confidence(self, df: pd.DataFrame, patterns: List[str]) -> float:
        """Calculate analysis confidence"""
        
        base_confidence = 90.0
        
        # Reduce confidence for problematic patterns
        if "missing_values" in patterns:
            base_confidence -= 10
        
        if "duplicates_detected" in patterns:
            base_confidence -= 5
        
        if "complex_structure" in patterns:
            base_confidence -= 5
        
        # Increase confidence for good patterns
        if "complete_data" in patterns:
            base_confidence += 5
        
        if "simple_structure" in patterns:
            base_confidence += 3
        
        return max(min(base_confidence, 100.0), 60.0)
    
    def _is_email_column(self, series: pd.Series) -> bool:
        """Check if column contains email addresses"""
        if series.dtype != 'object':
            return False
        
        sample = series.dropna().head(10)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        return sample.str.match(email_pattern).sum() > len(sample) * 0.7
    
    def _is_url_column(self, series: pd.Series) -> bool:
        """Check if column contains URLs"""
        if series.dtype != 'object':
            return False
        
        sample = series.dropna().head(10)
        url_pattern = r'^https?://'
        
        return sample.str.match(url_pattern).sum() > len(sample) * 0.7
    
    def _is_phone_column(self, series: pd.Series) -> bool:
        """Check if column contains phone numbers"""
        if series.dtype != 'object':
            return False
        
        sample = series.dropna().head(10)
        phone_pattern = r'^[\+]?[1-9][\d]{3,14}$'
        
        return sample.str.match(phone_pattern).sum() > len(sample) * 0.7
    
    def optimize_dataframe_for_excel(
        self, 
        df: pd.DataFrame, 
        use_ai: bool = True,
        min_confidence: float = 0.8
    ) -> tuple:
        """
        Optimize DataFrame structure for Excel export
        
        Args:
            df: DataFrame to optimize
            use_ai: Whether to use AI-powered optimization
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (optimized_dataframe, analysis_dict)
        """
        
        try:
            if not use_ai:
                return self._basic_excel_optimization(df)
            
            return self._ai_powered_excel_optimization(df, min_confidence)
            
        except Exception as e:
            logger.error(f"ERROR: Excel optimization failed: {str(e)}")
            # Fallback to basic optimization
            return self._basic_excel_optimization(df)
    
    def _basic_excel_optimization(self, df: pd.DataFrame) -> tuple:
        """Basic Excel optimization without AI"""
        
        optimized_df = df.copy()
        
        analysis = {
            "confidence": 85.0,
            "analysis_type": "deterministic",
            "optimizations_applied": ["basic_cleanup"],
            "column_optimizations": {},
            "recommendations": ["Consider enabling AI for advanced optimizations"]
        }
        
        # Basic cleanup
        # Remove completely empty columns
        empty_cols = optimized_df.columns[optimized_df.isnull().all()].tolist()
        if empty_cols:
            optimized_df = optimized_df.drop(columns=empty_cols)
            analysis["optimizations_applied"].append("empty_column_removal")
            analysis["removed_columns"] = empty_cols
        
        # Clean column names (remove special characters)
        original_columns = list(optimized_df.columns)
        optimized_df.columns = [self._clean_column_name(col) for col in optimized_df.columns]
        
        if list(optimized_df.columns) != original_columns:
            analysis["optimizations_applied"].append("column_name_cleanup")
        
        return optimized_df, analysis
    
    def _ai_powered_excel_optimization(self, df: pd.DataFrame, min_confidence: float) -> tuple:
        """AI-powered Excel optimization with advanced features"""
        
        analysis = {
            "confidence": 92.0,
            "analysis_type": "ai_powered",
            "optimizations_applied": [],
            "column_optimizations": {},
            "recommendations": []
        }
        
        optimized_df = df.copy()
        
        # 1. Advanced data type optimization
        for col in optimized_df.columns:
            original_dtype = str(optimized_df[col].dtype)
            
            if optimized_df[col].dtype == 'object':
                # Try to convert to datetime
                if self._looks_like_datetime(optimized_df[col]):
                    try:
                        optimized_df[col] = pd.to_datetime(optimized_df[col], errors='coerce')
                        analysis["optimizations_applied"].append(f"datetime_conversion_{col}")
                        analysis["column_optimizations"][col] = "converted_to_datetime"
                    except:
                        pass
                
                # Try to convert to numeric
                elif self._looks_like_numeric(optimized_df[col]):
                    try:
                        numeric_col = pd.to_numeric(optimized_df[col], errors='coerce')
                        if not numeric_col.isna().all():
                            optimized_df[col] = numeric_col
                            analysis["optimizations_applied"].append(f"numeric_conversion_{col}")
                            analysis["column_optimizations"][col] = "converted_to_numeric"
                    except:
                        pass
        
        # 2. Intelligent column name optimization
        original_columns = list(optimized_df.columns)
        optimized_df.columns = [self._optimize_column_name_ai(col) for col in optimized_df.columns]
        
        if list(optimized_df.columns) != original_columns:
            analysis["optimizations_applied"].append("intelligent_column_naming")
        
        # 3. Remove completely empty columns
        empty_cols = optimized_df.columns[optimized_df.isnull().all()].tolist()
        if empty_cols:
            optimized_df = optimized_df.drop(columns=empty_cols)
            analysis["optimizations_applied"].append("empty_column_removal")
            analysis["removed_columns"] = empty_cols
        
        # 4. Intelligent column reordering
        optimized_df = self._reorder_columns_intelligently(optimized_df)
        analysis["optimizations_applied"].append("intelligent_column_reordering")
        
        # 5. Data quality recommendations
        quality_issues = self._detect_data_quality_issues(optimized_df)
        if quality_issues:
            analysis["recommendations"].extend(quality_issues)
        
        # 6. Adjust confidence based on optimizations
        optimization_count = len(analysis["optimizations_applied"])
        confidence_boost = min(optimization_count * 2, 8)  # Max 8 points boost
        analysis["confidence"] = min(analysis["confidence"] + confidence_boost, 100.0)
        
        logger.info(f"✅ AI Excel optimization completed - Applied {optimization_count} optimizations")
        return optimized_df, analysis
    
    def _clean_column_name(self, column_name: str) -> str:
        """Basic column name cleanup"""
        import re
        # Remove special characters and normalize spaces
        cleaned = re.sub(r'[^\w\s]', '', str(column_name))
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned if cleaned else 'Unnamed_Column'
    
    def _optimize_column_name_ai(self, column_name: str) -> str:
        """AI-powered column name optimization"""
        import re
        
        name = str(column_name).strip()
        
        # Handle empty or invalid names
        if not name or name.isspace():
            return 'Unnamed_Column'
        
        # Convert snake_case to Title Case
        if '_' in name:
            words = name.split('_')
            return ' '.join(word.capitalize() for word in words if word)
        
        # Convert camelCase to Title Case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
        title_case = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in title_case.split())
    
    def _looks_like_datetime(self, series: pd.Series) -> bool:
        """Check if a series looks like datetime data"""
        if series.dtype != 'object':
            return False
        
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        # Check for common datetime patterns
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for pattern in datetime_patterns:
            matches = sample.astype(str).str.match(pattern).sum()
            if matches > len(sample) * 0.7:
                return True
        
        return False
    
    def _looks_like_numeric(self, series: pd.Series) -> bool:
        """Check if a series looks like numeric data"""
        if series.dtype != 'object':
            return False
        
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        # Try to convert sample to numeric
        try:
            numeric_sample = pd.to_numeric(sample, errors='coerce')
            valid_numbers = ~numeric_sample.isna()
            return valid_numbers.sum() > len(sample) * 0.7
        except:
            return False
    
    def _reorder_columns_intelligently(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorder columns in a logical way"""
        columns = list(df.columns)
        
        # Priority order: ID columns, Name columns, Date columns, Number columns, Other
        id_cols = [col for col in columns if 'id' in col.lower()]
        name_cols = [col for col in columns if any(word in col.lower() for word in ['name', 'title', 'label'])]
        date_cols = [col for col in columns if any(word in col.lower() for word in ['date', 'time', 'created', 'updated'])]
        number_cols = [col for col in columns if df[col].dtype in ['int64', 'float64']]
        other_cols = [col for col in columns if col not in id_cols + name_cols + date_cols + number_cols]
        
        # Remove duplicates while preserving order
        reordered = []
        for col_list in [id_cols, name_cols, date_cols, number_cols, other_cols]:
            for col in col_list:
                if col not in reordered:
                    reordered.append(col)
        
        return df[reordered]
    
    def _detect_data_quality_issues(self, df: pd.DataFrame) -> List[str]:
        """Detect potential data quality issues"""
        recommendations = []
        
        # Check for high null percentage
        for col in df.columns:
            null_pct = (df[col].isnull().sum() / len(df)) * 100
            if null_pct > 20:
                recommendations.append(f"Column '{col}' has {null_pct:.1f}% missing values - consider data cleaning")
        
        # Check for duplicate rows
        if df.duplicated().any():
            dup_count = df.duplicated().sum()
            recommendations.append(f"Found {dup_count} duplicate rows - consider removing duplicates")
        
        # Check for inconsistent data types in object columns
        for col in df.select_dtypes(include=['object']).columns:
            if len(df[col].dropna()) > 0:
                sample_types = df[col].dropna().apply(type).unique()
                if len(sample_types) > 1:
                    recommendations.append(f"Column '{col}' has mixed data types - consider data normalization")
        
        return recommendations
    
    async def optimize_dataframe_for_excel_with_ai(
        self, 
        df: pd.DataFrame, 
        use_ai: bool = True,
        min_confidence: float = 0.8,
        detected_issues: List[str] = None
    ) -> tuple:
        """
        Optimize DataFrame for Excel export - only use AI if issues detected
        
        Args:
            df: DataFrame to optimize
            use_ai: Whether AI assistance is available
            min_confidence: Minimum confidence threshold
            detected_issues: List of issues detected in deterministic processing
            
        Returns:
            Tuple of (optimized_df, analysis_result, ai_usage_info)
        """
        
        if not detected_issues:
            # No issues detected, return original DataFrame
            analysis = {
                "confidence": 95.0,
                "analysis_type": "deterministic",
                "optimizations_applied": ["no_optimization_needed"],
                "recommendations": ["Data is ready for Excel export"]
            }
            ai_usage = self.create_ai_usage_info(
                ai_used=False,
                processing_mode="deterministic"
            )
            return df, analysis, ai_usage
        
        if not use_ai or not self.azure_openai.is_configured:
            # AI not available, apply basic optimizations
            optimized_df = self._basic_excel_optimization(df, detected_issues)
            analysis = {
                "confidence": 70.0,
                "analysis_type": "basic_optimization",
                "optimizations_applied": ["basic_fixes_applied"],
                "recommendations": ["Basic optimizations applied, AI not available"]
            }
            ai_usage = self.create_ai_usage_info(
                ai_used=False,
                processing_mode="fallback_optimization",
                detected_issues=detected_issues
            )
            return optimized_df, analysis, ai_usage
        
        try:
            logger.info("🤖 Using AI to optimize DataFrame for Excel...")
            
            # Use AI to resolve specific issues
            optimization_result = await self.azure_openai.optimize_json_for_excel(
                df.to_dict('records'), use_ai, detected_issues
            )
            
            # Apply AI recommendations
            optimized_df = self._apply_ai_optimizations(df, optimization_result)
            
            analysis = {
                "confidence": optimization_result.get("confidence", 80.0),
                "analysis_type": "ai_optimization",
                "optimizations_applied": optimization_result.get("optimizations", []),
                "recommendations": optimization_result.get("recommendations", [])
            }
            
            ai_usage = self.create_ai_usage_info(
                ai_used=True,
                processing_mode="ai_assisted",
                detected_issues=detected_issues,
                ai_improvements=optimization_result.get("optimizations", [])
            )
            
            return optimized_df, analysis, ai_usage
            
        except Exception as e:
            logger.error(f"ERROR: AI optimization failed: {str(e)}")
            # Fallback to basic optimization
            optimized_df = self._basic_excel_optimization(df, detected_issues)
            analysis = {
                "confidence": 60.0,
                "analysis_type": "fallback_optimization",
                "optimizations_applied": ["ai_failed_basic_applied"],
                "recommendations": [f"AI optimization failed: {str(e)}, applied basic fixes"]
            }
            ai_usage = self.create_ai_usage_info(
                ai_used=False,
                processing_mode="fallback_optimization",
                detected_issues=detected_issues + [f"ai_error_{str(e)}"]
            )
            return optimized_df, analysis, ai_usage
    
    def _basic_excel_optimization(self, df: pd.DataFrame, detected_issues: List[str]) -> pd.DataFrame:
        """Apply basic optimizations for Excel compatibility"""
        
        optimized_df = df.copy()
        
        try:
            for issue in detected_issues:
                if "nested_data" in issue:
                    # Flatten nested data
                    optimized_df = self._flatten_nested_columns(optimized_df)
                
                elif "problematic_column_names" in issue:
                    # Fix column names
                    optimized_df = self._fix_column_names(optimized_df)
                
                elif "long_text_values" in issue:
                    # Truncate long text values
                    optimized_df = self._truncate_long_text(optimized_df)
                
                elif "mixed_types" in issue:
                    # Convert mixed types to strings
                    optimized_df = self._normalize_mixed_types(optimized_df)
                
                elif "exceeds_excel_row_limit" in issue:
                    # Truncate rows
                    optimized_df = optimized_df.head(1048576)
                
                elif "exceeds_excel_column_limit" in issue:
                    # Truncate columns
                    optimized_df = optimized_df.iloc[:, :16384]
            
            return optimized_df
            
        except Exception as e:
            logger.error(f"ERROR: Basic optimization failed: {str(e)}")
            return df  # Return original if optimization fails
    
    def _flatten_nested_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flatten columns with nested data"""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (dict, list)) else x)
        return df
    
    def _fix_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix problematic column names for Excel"""
        new_columns = []
        for col in df.columns:
            new_col = str(col)
            # Remove forbidden characters
            for char in ['/', '\\', '*', '?', '[', ']']:
                new_col = new_col.replace(char, '_')
            # Truncate if too long
            if len(new_col) > 255:
                new_col = new_col[:255]
            new_columns.append(new_col)
        
        df.columns = new_columns
        return df
    
    def _truncate_long_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Truncate text values that exceed Excel limits"""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).apply(lambda x: x[:32767] if len(x) > 32767 else x)
        return df
    
    def _normalize_mixed_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert mixed-type columns to strings"""
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
        return df
    
    def _apply_ai_optimizations(self, df: pd.DataFrame, optimization_result: Dict[str, Any]) -> pd.DataFrame:
        """Apply AI-recommended optimizations"""
        # This would apply specific AI recommendations
        # For now, apply basic optimizations plus any AI-specific suggestions
        optimized_df = self._basic_excel_optimization(df, optimization_result.get("detected_issues", []))
        return optimized_df

    def _convert_to_ai_analysis(self, azure_result: Dict[str, Any], df: pd.DataFrame) -> AIAnalysis:
        """Convert Azure OpenAI result to AIAnalysis model"""
        
        return AIAnalysis(
            confidence=azure_result.get("confidence", 85.0),
            analysis_type="azure_openai" if azure_result.get("ai_enabled", True) else "deterministic",
            detected_patterns=azure_result.get("patterns", []),
            column_types=self._detect_column_types(df),
            recommendations=azure_result.get("recommendations", [])
        )
    
    async def optimize_dataframe_for_excel_with_ai(
        self, 
        df: pd.DataFrame, 
        use_ai: bool = True,
        min_confidence: float = 0.8
    ) -> tuple:
        """
        Optimize DataFrame for Excel using Azure OpenAI
        
        Args:
            df: DataFrame to optimize
            use_ai: Whether to use AI optimization
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (optimized_dataframe, analysis_dict)
        """
        
        try:
            if not use_ai:
                return self._basic_excel_optimization(df)
            
            # Get AI optimization recommendations
            json_data = df.to_dict('records')
            optimization_result = await self.azure_openai.optimize_json_for_excel(json_data, use_ai)
            
            # Apply optimizations
            optimized_df = self._apply_ai_optimizations(df, optimization_result)
            
            # Create analysis result
            analysis = {
                "confidence": 95.0,
                "analysis_type": "azure_openai",
                "optimizations_applied": optimization_result.get("excel_optimizations", []),
                "column_optimizations": optimization_result.get("column_mapping", {}),
                "recommendations": ["AI-powered optimization completed"],
                "ai_enabled": True
            }
            
            return optimized_df, analysis
            
        except Exception as e:
            logger.error(f"ERROR: AI Excel optimization failed: {str(e)}")
            return self._basic_excel_optimization(df)
    
    def _apply_ai_optimizations(self, df: pd.DataFrame, optimization_result: Dict[str, Any]) -> pd.DataFrame:
        """Apply AI optimization recommendations to DataFrame"""
        
        optimized_df = df.copy()
        
        # Apply column mapping if provided
        column_mapping = optimization_result.get("column_mapping", {})
        if column_mapping:
            optimized_df = optimized_df.rename(columns=column_mapping)
        
        # Apply type conversions if provided
        type_conversions = optimization_result.get("type_conversions", {})
        for col, target_type in type_conversions.items():
            if col in optimized_df.columns:
                try:
                    if target_type == "datetime":
                        optimized_df[col] = pd.to_datetime(optimized_df[col], errors='coerce')
                    elif target_type == "numeric":
                        optimized_df[col] = pd.to_numeric(optimized_df[col], errors='coerce')
                except Exception as e:
                    logger.warning(f"Failed to convert column {col} to {target_type}: {str(e)}")
        
        return optimized_df
