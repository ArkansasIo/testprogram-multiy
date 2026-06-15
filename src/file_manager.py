"""
File Manager Module
Handles file and folder operations for the IDE Compiler Manager
"""
import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional

class FileManager:
    """Manages files and folders for compilation projects"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)
        
    def create_project(self, project_name: str) -> Path:
        """Create a new project directory"""
        project_path = self.project_root / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard subdirectories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "resources").mkdir(exist_ok=True)
        (project_path / "libs").mkdir(exist_ok=True)
        
        # Create project config
        config = {
            "name": project_name,
            "version": "1.0.0",
            "entry_point": "main.py",
            "output_name": f"{project_name}.exe",
            "include_files": [],
            "dependencies": []
        }
        
        with open(project_path / "project.json", "w") as f:
            json.dump(config, f, indent=4)
            
        return project_path
    
    def add_file(self, project_name: str, file_path: str, content: str = "") -> bool:
        """Add a file to the project"""
        try:
            project_path = self.project_root / project_name
            target_file = project_path / file_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error adding file: {e}")
            return False
    
    def add_folder(self, project_name: str, folder_path: str) -> bool:
        """Add a folder to the project"""
        try:
            project_path = self.project_root / project_name
            target_folder = project_path / folder_path
            target_folder.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error adding folder: {e}")
            return False
    
    def import_files(self, project_name: str, source_paths: List[str]) -> bool:
        """Import multiple files/folders into the project"""
        try:
            project_path = self.project_root / project_name / "src"
            
            for source in source_paths:
                source_path = Path(source)
                if source_path.is_file():
                    shutil.copy2(source_path, project_path / source_path.name)
                elif source_path.is_dir():
                    shutil.copytree(source_path, project_path / source_path.name, dirs_exist_ok=True)
            return True
        except Exception as e:
            print(f"Error importing files: {e}")
            return False
    
    def list_project_files(self, project_name: str) -> List[str]:
        """List all files in a project"""
        project_path = self.project_root / project_name
        files = []
        
        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(project_path)
                files.append(str(relative_path))
        
        return files
    
    def get_project_config(self, project_name: str) -> Optional[Dict]:
        """Get project configuration"""
        try:
            config_path = self.project_root / project_name / "project.json"
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading config: {e}")
            return None
    
    def update_project_config(self, project_name: str, config: Dict) -> bool:
        """Update project configuration"""
        try:
            config_path = self.project_root / project_name / "project.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error updating config: {e}")
            return False
    
    def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        try:
            project_path = self.project_root / project_name
            if project_path.exists():
                shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False

# Made with Bob
