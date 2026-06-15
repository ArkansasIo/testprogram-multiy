# Quick Start Guide

Get started with IDE Compiler Manager in 5 minutes!

## Step 1: Setup (First Time Only)

Run the setup script:

```bash
setup.bat
```

This will install PyInstaller and other dependencies.

## Step 2: Start the IDE

### Option A: GUI Mode (Easy)

Double-click `run.bat` or run:

```bash
python main.py
```

### Option B: CLI Mode (Advanced)

```bash
python src/cli.py --help
```

## Step 3: Create Your First Project

### Using GUI:

1. Click **File** → **New Project**
2. Enter project name (e.g., "MyFirstApp")
3. Click **Create**

### Using CLI:

```bash
python src/cli.py create MyFirstApp
```

## Step 4: Add Your Code

### Using GUI:

1. Select your project from the list
2. Click **Add Files** button
3. Select your Python files
4. Or click **Add Folder** to import entire folders

### Using CLI:

```bash
python src/cli.py add MyFirstApp main.py utils.py
```

### Or Create Files Manually:

Navigate to `projects/MyFirstApp/src/` and create your files there.

**Example main.py:**

```python
def main():
    print("Hello from My First App!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
```

## Step 5: Configure Project

### Using GUI:

1. Select your project
2. Set **Entry Point**: `main.py` (your main file)
3. Set **Output Name**: `MyFirstApp.exe`
4. Click **Update Config**

### Using CLI:

Edit `projects/MyFirstApp/project.json`:

```json
{
    "name": "MyFirstApp",
    "version": "1.0.0",
    "entry_point": "main.py",
    "output_name": "MyFirstApp.exe"
}
```

## Step 6: Compile to EXE

### Using GUI:

1. Select your project
2. Choose options:
   - ✅ **Single File EXE** (recommended)
   - ✅ **Show Console** (for debugging)
3. Click **Compile Current**
4. Wait for compilation (check console output)
5. Find your EXE in the `output/` folder

### Using CLI:

```bash
python src/cli.py compile MyFirstApp
```

## Step 7: Test Your EXE

Navigate to the `output/` folder and double-click your executable!

```
ide-compiler-manager/
└── output/
    └── MyFirstApp.exe  ← Your compiled program!
```

## Common Tasks

### Compile Multiple Projects

**GUI:** Click **Build** → **Compile All Projects**

**CLI:**
```bash
python src/cli.py compile-all
```

### Create a Bundle

Package multiple executables together:

**GUI:** Click **Build** → **Create Bundle**

**CLI:**
```bash
python src/cli.py bundle MyToolkit
```

### View Project Files

**GUI:** Click **View Files** button

**CLI:**
```bash
python src/cli.py list
```

## Try the Demo

We've included a demo calculator. Try it:

### Using GUI:

1. Create new project: "Calculator"
2. Copy `templates/demo_calculator.py` to `projects/Calculator/src/main.py`
3. Set entry point to `main.py`
4. Compile!

### Using CLI:

```bash
# Create project
python src/cli.py create Calculator

# Copy demo file
copy templates\demo_calculator.py projects\Calculator\src\main.py

# Compile
python src/cli.py compile Calculator
```

## Troubleshooting

### "PyInstaller not found"

Run setup again:
```bash
setup.bat
```

Or install manually:
```bash
pip install pyinstaller
```

### "Entry point not found"

Make sure your main Python file exists in `projects/YourProject/src/`

### Compilation takes long time

This is normal for first compilation. Subsequent compilations are faster.

### EXE is very large

This is normal. PyInstaller bundles Python and all dependencies.

## Tips

1. **Test your code first** - Run it normally before compiling
2. **Use relative paths** - Avoid absolute paths in your code
3. **Include resources** - Put data files in `resources/` folder
4. **Check console output** - It shows what's happening during compilation
5. **Start simple** - Begin with a basic "Hello World" program

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Explore compilation options (windowed mode, icons, etc.)
- Create multiple projects and bundle them
- Share your compiled programs!

## Need Help?

Check the console output for error messages. Most issues are related to:
- Missing files
- Import errors
- Path problems

---

**Happy Coding! 🎉**