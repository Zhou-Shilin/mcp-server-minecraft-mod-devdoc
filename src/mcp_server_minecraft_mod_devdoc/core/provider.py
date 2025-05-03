"""
Base class for documentation providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class DocProvider(ABC):
    """
    Base class for documentation providers
    """
    
    @abstractmethod
    def get_versions(self) -> str:
        """
        Get a list of available documentation versions
        
        Returns:
            A string containing the list of available versions
        """
        pass
    
    @abstractmethod
    def get_structure(self, version: str) -> str:
        """
        Get the file structure for a specific version of documentation
        
        Args:
            version: The version of the documentation
            
        Returns:
            A string containing the file structure
        """
        pass
    
    @abstractmethod
    def get_preview(self, version: str, file_path: str) -> str:
        """
        Get a preview of a documentation file
        
        Args:
            version: The version of the documentation
            file_path: The path to the file
            
        Returns:
            A string containing the preview of the file
        """
        pass
    
    @abstractmethod
    def get_full_content(self, version: str, file_path: str) -> str:
        """
        Get the full content of a documentation file
        
        Args:
            version: The version of the documentation
            file_path: The path to the file
            
        Returns:
            A string containing the full content of the file
        """
        pass
