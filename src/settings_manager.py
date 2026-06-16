"""
Settings Manager Module
Handles IDE preferences, settings persistence, and configuration
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class EditorSettings:
    """Editor-specific settings"""
    font_family: str = "Consolas"
    font_size: int = 11
    tab_size: int = 4
    use_spaces: bool = True
    wrap_text: bool = False
    show_line_numbers: bool = True
    highlight_current_line: bool = True
    show_indentation_guides: bool = True
    auto_indent: bool = True
    auto_close_brackets: bool = True
    match_brackets: bool = True
    syntax_highlighting: bool = True
    code_folding: bool = True
    minimap_enabled: bool = False
    theme: str = "dark"
    color_scheme: str = "monokai"

@dataclass
class BuildSettings:
    """Build/compilation settings"""
    default_onefile: bool = True
    default_console: bool = True
    clean_build: bool = True
    parallel_builds: bool = False
    max_parallel_builds: int = 4
    output_directory: str = "output"
    auto_build_on_save: bool = False
    compression_level: str = "normal"  # fast, normal, maximum
    include_debug_info: bool = False
    optimization_level: str = "balanced"

@dataclass
class GeneralSettings:
    """General IDE settings"""
    language: str = "en"
    auto_save: bool = False
    auto_save_interval: int = 30  # seconds
    confirm_exit: bool = True
    recent_files_limit: int = 10
    recent_projects_limit: int = 10
    restore_last_session: bool = True
    check_updates: bool = True
    telemetry: bool = False
    window_geometry: str = ""
    window_state: str = "normal"  # normal, maximized, minimized

@dataclass
class ProjectSettings:
    """Default project settings"""
    default_entry_point: str = "main.py"
    default_output_name: str = "{project}.exe"
    create_resources_dir: bool = True
    create_libs_dir: bool = True
    create_tests_dir: bool = False
    create_docs_dir: bool = False
    default_version: str = "1.0.0"
    add_gitignore: bool = True
    add_readme: bool = False
    add_license: bool = False

@dataclass
class IDESettings:
    """Complete IDE settings container"""
    general: GeneralSettings = field(default_factory=GeneralSettings)
    editor: EditorSettings = field(default_factory=EditorSettings)
    build: BuildSettings = field(default_factory=BuildSettings)
    project: ProjectSettings = field(default_factory=ProjectSettings)
    custom_commands: Dict[str, str] = field(default_factory=dict)
    recent_projects: List[str] = field(default_factory=list)
    recent_files: List[str] = field(default_factory=list)
    keybindings: Dict[str, str] = field(default_factory=dict)


class SettingsManager:
    """Manages IDE settings persistence and access"""
    
    DEFAULT_CONFIG_FILE = "ide_settings.json"
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or self.DEFAULT_CONFIG_FILE)
        self.settings = IDESettings()
        self.load()
    
    def load(self) -> bool:
        """Load settings from config file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                
                # Restore dataclass fields
                if "general" in data:
                    self.settings.general = GeneralSettings(**data["general"])
                if "editor" in data:
                    self.settings.editor = EditorSettings(**data["editor"])
                if "build" in data:
                    self.settings.build = BuildSettings(**data["build"])
                if "project" in data:
                    self.settings.project = ProjectSettings(**data["project"])
                if "custom_commands" in data:
                    self.settings.custom_commands = data["custom_commands"]
                if "recent_projects" in data:
                    self.settings.recent_projects = data["recent_projects"]
                if "recent_files" in data:
                    self.settings.recent_files = data["recent_files"]
                if "keybindings" in data:
                    self.settings.keybindings = data["keybindings"]
                
                return True
            return False
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def save(self) -> bool:
        """Save settings to config file"""
        try:
            data = {
                "general": asdict(self.settings.general),
                "editor": asdict(self.settings.editor),
                "build": asdict(self.settings.build),
                "project": asdict(self.settings.project),
                "custom_commands": self.settings.custom_commands,
                "recent_projects": self.settings.recent_projects,
                "recent_files": self.settings.recent_files,
                "keybindings": self.settings.keybindings
            }
            
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def add_recent_project(self, project_path: str):
        """Add a project to recent list"""
        if project_path in self.settings.recent_projects:
            self.settings.recent_projects.remove(project_path)
        self.settings.recent_projects.insert(0, project_path)
        limit = self.settings.general.recent_projects_limit
        self.settings.recent_projects = self.settings.recent_projects[:limit]
        self.save()
    
    def add_recent_file(self, file_path: str):
        """Add a file to recent list"""
        if file_path in self.settings.recent_files:
            self.settings.recent_files.remove(file_path)
        self.settings.recent_files.insert(0, file_path)
        limit = self.settings.general.recent_files_limit
        self.settings.recent_files = self.settings.recent_files[:limit]
        self.save()
    
    def get_setting(self, category: str, key: str, default=None):
        """Get a specific setting value"""
        try:
            category_obj = getattr(self.settings, category, None)
            if category_obj:
                return getattr(category_obj, key, default)
            return default
        except:
            return default
    
    def set_setting(self, category: str, key: str, value):
        """Set a specific setting value"""
        try:
            category_obj = getattr(self.settings, category, None)
            if category_obj:
                setattr(category_obj, key, value)
                self.save()
                return True
            return False
        except:
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = IDESettings()
        return self.save()

# Made with Bob