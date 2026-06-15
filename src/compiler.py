"""
Compiler Module
Handles compilation of multiple files and folders into a single executable
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import shutil

class Compiler:
    """Compiles projects into standalone executables"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required compilation tools are installed"""
        dependencies = {
            "pyinstaller": False,
            "python": False
        }
        
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            dependencies["python"] = result.returncode == 0
        except:
            pass
        
        # Check PyInstaller
        try:
            result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                                  capture_output=True, text=True)
            dependencies["pyinstaller"] = result.returncode == 0
        except:
            pass
        
        return dependencies
    
    def install_pyinstaller(self) -> bool:
        """Install PyInstaller if not present"""
        try:
            print("Installing PyInstaller...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error installing PyInstaller: {e}")
            return False
    
    def compile_to_exe(self, project_path: Path, config: Dict, 
                       onefile: bool = True, console: bool = True) -> Optional[Path]:
        """
        Compile project to executable using PyInstaller
        
        Args:
            project_path: Path to the project directory
            config: Project configuration dictionary
            onefile: Create a single executable file
            console: Show console window
        
        Returns:
            Path to the compiled executable or None if failed
        """
        try:
            # Check dependencies
            deps = self.check_dependencies()
            if not deps["python"]:
                print("Error: Python not found!")
                return None
            
            if not deps["pyinstaller"]:
                print("PyInstaller not found. Installing...")
                if not self.install_pyinstaller():
                    print("Failed to install PyInstaller!")
                    return None
            
            # Get entry point
            entry_point = project_path / "src" / config.get("entry_point", "main.py")
            if not entry_point.exists():
                print(f"Error: Entry point {entry_point} not found!")
                return None
            
            # Prepare PyInstaller command
            output_name = config.get("output_name", "program.exe")
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                f"--distpath={self.output_dir}",
                f"--workpath={project_path / 'build'}",
                f"--specpath={project_path}",
                f"--name={output_name.replace('.exe', '')}"
            ]
            
            # Add options
            if onefile:
                cmd.append("--onefile")
            
            if not console:
                cmd.append("--windowed")
            
            # Add additional files and folders
            src_dir = project_path / "src"
            for item in src_dir.rglob("*"):
                if item.is_file() and item != entry_point:
                    relative_path = item.relative_to(src_dir)
                    cmd.append(f"--add-data={item};{relative_path.parent}")
            
            # Add resources folder if exists
            resources_dir = project_path / "resources"
            if resources_dir.exists():
                cmd.append(f"--add-data={resources_dir};resources")
            
            # Add libraries folder if exists
            libs_dir = project_path / "libs"
            if libs_dir.exists():
                for lib_file in libs_dir.rglob("*.py"):
                    cmd.append(f"--hidden-import={lib_file.stem}")
            
            # Add entry point at the end
            cmd.append(str(entry_point))
            
            print(f"Compiling {config['name']}...")
            print(f"Command: {' '.join(cmd)}")
            
            # Run PyInstaller
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_path)
            
            if result.returncode == 0:
                exe_path = self.output_dir / output_name
                if not exe_path.exists():
                    exe_path = self.output_dir / f"{output_name.replace('.exe', '')}.exe"
                
                if exe_path.exists():
                    print(f"[OK] Compilation successful: {exe_path}")
                    return exe_path
                else:
                    print("Warning: Compilation completed but executable not found at expected location")
                    # Search for the executable
                    for file in self.output_dir.rglob("*.exe"):
                        print(f"Found executable: {file}")
                        return file
            else:
                print(f"Compilation failed!")
                print(f"Error output:\n{result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error during compilation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def compile_multiple_projects(self, projects: List[tuple]) -> List[Path]:
        """
        Compile multiple projects
        
        Args:
            projects: List of (project_path, config) tuples
        
        Returns:
            List of paths to compiled executables
        """
        compiled = []
        
        for project_path, config in projects:
            print(f"\n{'='*60}")
            print(f"Compiling project: {config['name']}")
            print(f"{'='*60}")
            
            exe_path = self.compile_to_exe(project_path, config)
            if exe_path:
                compiled.append(exe_path)
        
        return compiled
    
    def create_bundle(self, executables: List[Path], bundle_name: str) -> Optional[Path]:
        """
        Create a bundle of multiple executables
        
        Args:
            executables: List of executable paths
            bundle_name: Name for the bundle directory
        
        Returns:
            Path to the bundle directory
        """
        try:
            bundle_path = self.output_dir / bundle_name
            bundle_path.mkdir(parents=True, exist_ok=True)
            
            for exe in executables:
                if exe.exists():
                    shutil.copy2(exe, bundle_path / exe.name)
            
            print(f"[OK] Bundle created: {bundle_path}")
            return bundle_path
            
        except Exception as e:
            print(f"Error creating bundle: {e}")
            return None

# Made with Bob
