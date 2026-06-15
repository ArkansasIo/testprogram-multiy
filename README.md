# IDE Compiler Manager

A comprehensive IDE program manager that compiles multiple files and folders into single executable programs. Build, manage, and bundle multiple projects into standalone EXE files.

## Features

- ✅ **Multi-Project Management**: Create and manage multiple projects
- ✅ **File & Folder Organization**: Add files, folders, and import external resources
- ✅ **Single EXE Compilation**: Compile entire projects into standalone executables
- ✅ **Batch Compilation**: Compile multiple projects at once
- ✅ **Bundle Creation**: Package multiple executables together
- ✅ **GUI Interface**: User-friendly graphical interface
- ✅ **CLI Support**: Command-line interface for automation
- ✅ **Cross-Platform**: Works on Windows, Linux, and macOS

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Navigate to the `ide-compiler-manager` directory
2. Install dependencies:
   ```bash
   pip install pyinstaller
   ```

## Usage

### GUI Mode (Recommended)

Run the graphical interface:

```bash
python main.py
```

#### GUI Features:

1. **Create New Project**: Click "File" → "New Project"
2. **Add Files**: Select a project, then click "Add Files" or "Add Folder"
3. **Configure Project**: Set entry point and output name
4. **Compile**: Click "Compile Current" or "Compile All"
5. **Create Bundle**: Package multiple executables together

### CLI Mode

Use the command-line interface for automation:

```bash
# Create a new project
python src/cli.py create MyProject

# List all projects
python src/cli.py list

# Add files to a project
python src/cli.py add MyProject file1.py file2.py folder/

# Compile a project
python src/cli.py compile MyProject

# Compile all projects
python src/cli.py compile-all

# Create a bundle
python src/cli.py bundle MyBundle
```

## Project Structure

```
ide-compiler-manager/
├── main.py                 # GUI entry point
├── src/
│   ├── file_manager.py     # File and folder management
│   ├── compiler.py         # Compilation engine
│   ├── ide_gui.py          # GUI interface
│   └── cli.py              # CLI interface
├── projects/               # Your projects (created automatically)
├── output/                 # Compiled executables
├── templates/              # Example templates
└── README.md              # This file
```

## How It Works

### 1. Project Creation

When you create a project, the system:
- Creates a project directory with standard structure
- Generates a `project.json` configuration file
- Sets up `src/`, `resources/`, and `libs/` folders

### 2. File Management

Add files and folders to your project:
- **Add Files**: Copy individual files to the project
- **Add Folder**: Import entire folder structures
- **Import External**: Bring in files from anywhere on your system

### 3. Compilation

The compiler:
- Uses PyInstaller to bundle Python code
- Includes all project files and dependencies
- Creates a standalone executable
- Supports both single-file and directory output

### 4. Multi-Project Compilation

Compile multiple projects in one go:
- Processes each project sequentially
- Generates separate executables for each
- Reports success/failure for each project

### 5. Bundle Creation

Package multiple executables:
- Collects all compiled executables
- Creates a single directory containing all programs
- Useful for distributing multiple tools together

## Configuration

Each project has a `project.json` file:

```json
{
    "name": "MyProject",
    "version": "1.0.0",
    "entry_point": "main.py",
    "output_name": "MyProject.exe",
    "include_files": [],
    "dependencies": []
}
```

### Configuration Options:

- **name**: Project name
- **version**: Project version
- **entry_point**: Main Python file to execute
- **output_name**: Name of the compiled executable
- **include_files**: Additional files to include
- **dependencies**: Python packages required

## Compilation Options

### Single File vs Directory

- **Single File** (--onefile): Creates one executable file
  - Pros: Easy to distribute, single file
  - Cons: Slower startup, larger file size

- **Directory**: Creates a folder with executable and dependencies
  - Pros: Faster startup, smaller main file
  - Cons: Multiple files to distribute

### Console vs Windowed

- **Console**: Shows command prompt window
  - Use for: CLI tools, scripts, debugging

- **Windowed** (--no-console): Hides console window
  - Use for: GUI applications

## Examples

### Example 1: Simple Calculator

```python
# Create project
python src/cli.py create Calculator

# Add main file
# (Create calculator.py with your code)

# Compile
python src/cli.py compile Calculator
```

### Example 2: Multiple Tools Bundle

```python
# Create multiple projects
python src/cli.py create Tool1
python src/cli.py create Tool2
python src/cli.py create Tool3

# Add files to each project
# (Add your code files)

# Compile all at once
python src/cli.py compile-all

# Create bundle
python src/cli.py bundle MyToolkit
```

## Troubleshooting

### PyInstaller Not Found

```bash
pip install pyinstaller
```

### Compilation Fails

1. Check that entry point file exists
2. Verify all imports are available
3. Check console output for specific errors
4. Ensure Python version compatibility

### Missing Dependencies

Add hidden imports in the compiler or install missing packages:

```bash
pip install missing-package
```

### Large Executable Size

- Use directory mode instead of single file
- Exclude unnecessary packages
- Use UPX compression (advanced)

## Advanced Usage

### Custom Compilation

Modify `src/compiler.py` to add custom PyInstaller options:

```python
cmd.append("--icon=myicon.ico")
cmd.append("--version-file=version.txt")
cmd.append("--uac-admin")
```

### Adding Resources

Place resources in the `resources/` folder:
- Images
- Data files
- Configuration files
- Documentation

### Including Libraries

Place Python libraries in the `libs/` folder for automatic inclusion.

## Tips & Best Practices

1. **Organize Your Code**: Use proper folder structure
2. **Test Before Compiling**: Run your code normally first
3. **Use Relative Paths**: Avoid absolute paths in your code
4. **Include All Resources**: Don't forget data files
5. **Version Control**: Keep track of project versions
6. **Backup Projects**: Save your source code separately

## System Requirements

- **OS**: Windows 7+, Linux, macOS 10.13+
- **Python**: 3.7 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for tools, varies by project

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure project structure is correct
4. Review PyInstaller documentation for advanced issues

## Version History

- **v1.0.0**: Initial release
  - Multi-project management
  - GUI and CLI interfaces
  - Single EXE compilation
  - Bundle creation

## Future Enhancements

- [ ] Icon customization
- [ ] Version information embedding
- [ ] Digital signature support
- [ ] Automatic dependency detection
- [ ] Build profiles
- [ ] Cloud compilation
- [ ] Plugin system

---

**Happy Compiling! 🚀**