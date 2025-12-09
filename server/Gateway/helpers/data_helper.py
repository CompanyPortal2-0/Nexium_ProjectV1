"""
Data Helper
===========
Handles file operations and communication with Data Service.

Responsibilities:
    - File upload operations
    - File retrieval operations
    - File listing operations
"""

import requests
import os
import logging
from typing import Dict, Any, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DataHelper:
    """
    Helper class for file/data operations.
    Communicates with the Data Service for file management.
    """
    
    DATA_SERVICE = os.getenv('DATA_SERVICE', 'localhost:7055')
    INTERNAL_API_KEY = os.getenv('INTERNAL_API_KEY', 'supersecretinternalkey')
    TIMEOUT = 30  # Longer timeout for file uploads
    
    # =================== UPLOAD OPERATIONS ===================
    
    @staticmethod
    def upload_file(file, user_email: str) -> Tuple[Dict[str, Any], int]:
        """
        Upload a file to the Data Service.
        
        Args:
            file: The file object from request.files
            user_email: Email of the user uploading the file
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            files = {'file': (file.filename, file.stream, file.content_type)}
            headers = {
                'X-User-Email': user_email,
                'X-Internal-Key': DataHelper.INTERNAL_API_KEY
            }

            
            response = requests.post(
                f'http://{DataHelper.DATA_SERVICE}/upload',
                
                files=files,
                headers=headers,
                timeout=DataHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upload file service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Upload file error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    # =================== READ OPERATIONS ===================
    
    @staticmethod
    def get_all_files() -> Tuple[Dict[str, Any], int]:
        """
        Get list of all files.
        
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            headers = {
                'X-Internal-Key': DataHelper.INTERNAL_API_KEY
            }
            
            response = requests.get(
                f'http://{DataHelper.DATA_SERVICE}/getAllfiles',
                headers=headers,
                timeout=DataHelper.TIMEOUT
            )
            return response.json(), response.status_code
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get all files service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503
        except Exception as e:
            logger.error(f"Get all files error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500
    
    @staticmethod
    def get_file(filename: str) -> Tuple[Any, int, str]:
        """
        Get a specific file by filename.
        
        Args:
            filename: The name of the file to retrieve
            
        Returns:
            Tuple of (file_content, status_code, content_type)
            For success: (binary_content, 200, 'application/octet-stream')
            For error: (error_dict, status_code, 'application/json')
        """
        try:
            headers = {
                'X-Internal-Key': DataHelper.INTERNAL_API_KEY
            }
            
            response = requests.get(
                f'http://{DataHelper.DATA_SERVICE}/file/get/{filename}',
                headers=headers,
                timeout=DataHelper.TIMEOUT
            )
            
            if response.status_code == 200:
                # Return binary content for successful file retrieval
                content_type = response.headers.get('Content-Type', 'application/octet-stream')
                return response.content, response.status_code, content_type
            else:
                # Return error response
                try:
                    return response.json(), response.status_code, 'application/json'
                except:
                    return {"success": False, "error": "Failed to retrieve file"}, response.status_code, 'application/json'
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Get file service error: {e}")
            return {"success": False, "error": f"Service communication error: {str(e)}"}, 503, 'application/json'
        except Exception as e:
            logger.error(f"Get file error: {e}")
            return {"success": False, "error": f"Internal error: {str(e)}"}, 500, 'application/json'
    
    # =================== ALIAS METHODS ===================
    # Short aliases for convenience
    
    @staticmethod
    def upload(file, user_email: str) -> Tuple[Dict[str, Any], int]:
        """Alias for upload_file"""
        return DataHelper.upload_file(file, user_email)
    
    @staticmethod
    def list_files() -> Tuple[Dict[str, Any], int]:
        """Alias for get_all_files"""
        return DataHelper.get_all_files()
    
    @staticmethod
    def download(filename: str) -> Tuple[Any, int, str]:
        """Alias for get_file"""
        return DataHelper.get_file(filename)
