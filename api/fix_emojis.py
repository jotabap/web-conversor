#!/usr/bin/env python3
import os
import re

# Directory to process
API_DIR = "."

# Files to process
FILES_TO_PROCESS = [
    "function_app.py",
    "services/converter_service.py",
    "services/ai_service.py",
    "services/azure_openai_service.py"
]

# Emoji patterns to remove
EMOJI_PATTERNS = {
    "🔍": "INFO:",
    "📝": "INFO:",
    "📊": "INFO:",
    "🗃️": "INFO:",
    "🔧": "INFO:",
    "❌": "ERROR:",
    "⚠️": "WARNING:",
    "💡": "INFO:",
    "🔢": "INFO:"
}

def fix_file(filepath):
    """Remove emojis from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace emojis with text prefixes
        for emoji, replacement in EMOJI_PATTERNS.items():
            content = content.replace(emoji, replacement)
        
        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed emojis in: {filepath}")
        else:
            print(f"No emojis found in: {filepath}")
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    """Main function"""
    for file_path in FILES_TO_PROCESS:
        full_path = os.path.join(API_DIR, file_path)
        if os.path.exists(full_path):
            fix_file(full_path)
        else:
            print(f"File not found: {full_path}")

if __name__ == "__main__":
    main()