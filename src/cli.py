"""
CLI Module
Command-line interface for the IDE Compiler Manager
"""
import sys
import argparse
from pathlib import Path
from file_manager import FileManager
from compiler import Compiler

class CLI:
    """Command-line interface for IDE Compiler Manager"""
    
    def __init__(self):
        self.file_manager = FileManager("projects")
        self.compiler = Compiler("output")
    
    def create_project(self, name: str):
        """Create a new project"""
        print(f"Creating project: {name}")
        project_path = self.file_manager.create_project(name)
        print(f"[OK] Project created at: {project_path}")
        return project_path
    
    def list_projects(self):
        """List all projects"""
        projects_dir = Path("projects")
        if not projects_dir.exists():
            print("No projects found")
            return
        
        print("\nAvailable Projects:")
        print("-" * 40)
        for project in projects_dir.iterdir():
            if project.is_dir() and (project / "project.json").exists():
                config = self.file_manager.get_project_config(project.name)
                if config:
                    print(f"  • {project.name}")
                    print(f"    Entry: {config.get('entry_point', 'N/A')}")
                    print(f"    Output: {config.get('output_name', 'N/A')}")
                    print()
    
    def add_files(self, project_name: str, files: list):
        """Add files to a project"""
        print(f"Adding files to project: {project_name}")
        success = self.file_manager.import_files(project_name, files)
        if success:
            print(f"[OK] Added {len(files)} file(s)")
        else:
            print("[ERROR] Failed to add files")
    
    def compile_project(self, project_name: str, onefile: bool = True, console: bool = True):
        """Compile a project"""
        print(f"\nCompiling project: {project_name}")
        print("=" * 60)
        
        project_path = Path("projects") / project_name
        if not project_path.exists():
            print(f"[ERROR] Project '{project_name}' not found")
            return None
        
        config = self.file_manager.get_project_config(project_name)
        if not config:
            print(f"[ERROR] Could not load project configuration")
            return None
        
        result = self.compiler.compile_to_exe(project_path, config, onefile, console)
        
        if result:
            print(f"\n[OK] Compilation successful!")
            print(f"Output: {result}")
        else:
            print(f"\n[ERROR] Compilation failed!")
        
        return result
    
    def compile_all(self):
        """Compile all projects"""
        print("\nCompiling all projects...")
        print("=" * 60)
        
        projects_dir = Path("projects")
        if not projects_dir.exists():
            print("No projects found")
            return
        
        projects = []
        for project in projects_dir.iterdir():
            if project.is_dir() and (project / "project.json").exists():
                config = self.file_manager.get_project_config(project.name)
                if config:
                    projects.append((project, config))
        
        if not projects:
            print("No valid projects found")
            return
        
        results = self.compiler.compile_multiple_projects(projects)
        print(f"\n[OK] Compiled {len(results)} out of {len(projects)} projects")
    
    def create_bundle(self, bundle_name: str):
        """Create a bundle of all executables"""
        print(f"\nCreating bundle: {bundle_name}")
        
        output_dir = Path("output")
        if not output_dir.exists():
            print("No output directory found")
            return
        
        executables = list(output_dir.glob("*.exe"))
        if not executables:
            print("No executables found")
            return
        
        result = self.compiler.create_bundle(executables, bundle_name)
        if result:
            print(f"[OK] Bundle created: {result}")
        else:
            print("[ERROR] Failed to create bundle")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="IDE Compiler Manager - Multi-project EXE builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new project
  python cli.py create MyProject
  
  # List all projects
  python cli.py list
  
  # Add files to a project
  python cli.py add MyProject file1.py file2.py
  
  # Compile a project
  python cli.py compile MyProject
  
  # Compile all projects
  python cli.py compile-all
  
  # Create a bundle
  python cli.py bundle MyBundle
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('name', help='Project name')
    
    # List projects
    subparsers.add_parser('list', help='List all projects')
    
    # Add files
    add_parser = subparsers.add_parser('add', help='Add files to a project')
    add_parser.add_argument('project', help='Project name')
    add_parser.add_argument('files', nargs='+', help='Files to add')
    
    # Compile project
    compile_parser = subparsers.add_parser('compile', help='Compile a project')
    compile_parser.add_argument('project', help='Project name')
    compile_parser.add_argument('--no-onefile', action='store_true', help='Create directory instead of single file')
    compile_parser.add_argument('--no-console', action='store_true', help='Hide console window')
    
    # Compile all
    subparsers.add_parser('compile-all', help='Compile all projects')
    
    # Create bundle
    bundle_parser = subparsers.add_parser('bundle', help='Create a bundle of executables')
    bundle_parser.add_argument('name', help='Bundle name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLI()
    
    if args.command == 'create':
        cli.create_project(args.name)
    elif args.command == 'list':
        cli.list_projects()
    elif args.command == 'add':
        cli.add_files(args.project, args.files)
    elif args.command == 'compile':
        cli.compile_project(args.project, not args.no_onefile, not args.no_console)
    elif args.command == 'compile-all':
        cli.compile_all()
    elif args.command == 'bundle':
        cli.create_bundle(args.name)

if __name__ == "__main__":
    main()

# Made with Bob
