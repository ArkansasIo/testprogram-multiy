"""
IDE GUI Module
Graphical User Interface for the IDE Compiler Manager
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from file_manager import FileManager
from compiler import Compiler

class IDECompilerGUI:
    """Main GUI for IDE Compiler Manager"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IDE Compiler Manager - Multi-Project EXE Builder")
        self.root.geometry("1000x700")
        
        # Initialize managers
        self.file_manager = FileManager("projects")
        self.compiler = Compiler("output")
        
        # Current project
        self.current_project = None
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Build menu
        build_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Build", menu=build_menu)
        build_menu.add_command(label="Compile Current Project", command=self.compile_current)
        build_menu.add_command(label="Compile All Projects", command=self.compile_all)
        build_menu.add_command(label="Create Bundle", command=self.create_bundle)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Project list
        left_panel = ttk.LabelFrame(main_frame, text="Projects", padding="5")
        left_panel.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Project listbox
        self.project_listbox = tk.Listbox(left_panel, width=30)
        self.project_listbox.pack(fill=tk.BOTH, expand=True)
        self.project_listbox.bind('<<ListboxSelect>>', self.on_project_select)
        
        # Project buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="New", command=self.new_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_project).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_projects).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Project details
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(2, weight=1)
        
        # Project info
        info_frame = ttk.LabelFrame(right_panel, text="Project Information", padding="5")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(info_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W)
        self.project_name_label = ttk.Label(info_frame, text="No project selected", font=('Arial', 10, 'bold'))
        self.project_name_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(info_frame, text="Entry Point:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.entry_point_var = tk.StringVar(value="main.py")
        ttk.Entry(info_frame, textvariable=self.entry_point_var, width=30).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        ttk.Label(info_frame, text="Output Name:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.output_name_var = tk.StringVar(value="program.exe")
        ttk.Entry(info_frame, textvariable=self.output_name_var, width=30).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        ttk.Button(info_frame, text="Update Config", command=self.update_config).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # File management
        file_frame = ttk.LabelFrame(right_panel, text="File Management", padding="5")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(file_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Import External", command=self.import_external).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="View Files", command=self.view_files).pack(side=tk.LEFT, padx=2)
        
        # Console output
        console_frame = ttk.LabelFrame(right_panel, text="Console Output", padding="5")
        console_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.console = scrolledtext.ScrolledText(console_frame, height=15, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Bottom panel - Compilation controls
        bottom_panel = ttk.Frame(main_frame)
        bottom_panel.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Compilation options
        options_frame = ttk.LabelFrame(bottom_panel, text="Compilation Options", padding="5")
        options_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.onefile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Single File EXE", variable=self.onefile_var).pack(side=tk.LEFT, padx=5)
        
        self.console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show Console", variable=self.console_var).pack(side=tk.LEFT, padx=5)
        
        # Build buttons
        build_frame = ttk.Frame(bottom_panel)
        build_frame.pack(side=tk.RIGHT)
        
        ttk.Button(build_frame, text="Compile Current", command=self.compile_current, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(build_frame, text="Compile All", command=self.compile_all, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(build_frame, text="Create Bundle", command=self.create_bundle, width=15).pack(side=tk.LEFT, padx=2)
        
        # Load projects
        self.refresh_projects()
    
    def log(self, message):
        """Log message to console"""
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.root.update()
    
    def refresh_projects(self):
        """Refresh project list"""
        self.project_listbox.delete(0, tk.END)
        projects_dir = Path("projects")
        if projects_dir.exists():
            for project in projects_dir.iterdir():
                if project.is_dir() and (project / "project.json").exists():
                    self.project_listbox.insert(tk.END, project.name)
    
    def new_project(self):
        """Create a new project"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Project Name:").pack(pady=(20, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        def create():
            name = name_var.get().strip()
            if name:
                self.log(f"Creating project: {name}")
                self.file_manager.create_project(name)
                self.refresh_projects()
                self.log(f"✓ Project '{name}' created successfully")
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Name", "Please enter a project name")
        
        ttk.Button(dialog, text="Create", command=create).pack(pady=10)
    
    def open_project(self):
        """Open project folder"""
        if self.current_project:
            project_path = Path("projects") / self.current_project
            import os
            os.startfile(project_path)
    
    def delete_project(self):
        """Delete selected project"""
        selection = self.project_listbox.curselection()
        if selection:
            project_name = self.project_listbox.get(selection[0])
            if messagebox.askyesno("Confirm Delete", f"Delete project '{project_name}'?"):
                self.file_manager.delete_project(project_name)
                self.refresh_projects()
                self.log(f"✓ Project '{project_name}' deleted")
    
    def on_project_select(self, event):
        """Handle project selection"""
        selection = self.project_listbox.curselection()
        if selection:
            self.current_project = self.project_listbox.get(selection[0])
            self.project_name_label.config(text=self.current_project)
            
            # Load config
            config = self.file_manager.get_project_config(self.current_project)
            if config:
                self.entry_point_var.set(config.get("entry_point", "main.py"))
                self.output_name_var.set(config.get("output_name", f"{self.current_project}.exe"))
            
            self.log(f"Selected project: {self.current_project}")
    
    def update_config(self):
        """Update project configuration"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        config = self.file_manager.get_project_config(self.current_project)
        if config:
            config["entry_point"] = self.entry_point_var.get()
            config["output_name"] = self.output_name_var.get()
            self.file_manager.update_project_config(self.current_project, config)
            self.log(f"✓ Configuration updated for '{self.current_project}'")
    
    def add_files(self):
        """Add files to project"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        files = filedialog.askopenfilenames(title="Select Files to Add")
        if files:
            for file in files:
                file_path = Path(file)
                self.file_manager.add_file(self.current_project, f"src/{file_path.name}", 
                                          file_path.read_text(encoding='utf-8', errors='ignore'))
            self.log(f"✓ Added {len(files)} file(s) to '{self.current_project}'")
    
    def add_folder(self):
        """Add folder to project"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        folder = filedialog.askdirectory(title="Select Folder to Add")
        if folder:
            folder_path = Path(folder)
            self.file_manager.import_files(self.current_project, [folder])
            self.log(f"✓ Added folder '{folder_path.name}' to '{self.current_project}'")
    
    def import_external(self):
        """Import external files/folders"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        paths = filedialog.askopenfilenames(title="Select Files/Folders to Import")
        if paths:
            self.file_manager.import_files(self.current_project, list(paths))
            self.log(f"✓ Imported {len(paths)} item(s) to '{self.current_project}'")
    
    def view_files(self):
        """View project files"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        files = self.file_manager.list_project_files(self.current_project)
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Files in {self.current_project}")
        dialog.geometry("500x400")
        
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for file in sorted(files):
            listbox.insert(tk.END, file)
    
    def compile_current(self):
        """Compile current project"""
        if not self.current_project:
            messagebox.showwarning("No Project", "Please select a project first")
            return
        
        self.log("\n" + "="*60)
        self.log(f"Starting compilation of '{self.current_project}'")
        self.log("="*60)
        
        def compile_thread():
            project_path = Path("projects") / self.current_project
            config = self.file_manager.get_project_config(self.current_project)
            
            if config:
                result = self.compiler.compile_to_exe(
                    project_path, config,
                    onefile=self.onefile_var.get(),
                    console=self.console_var.get()
                )
                
                if result:
                    self.log(f"✓ Compilation successful!")
                    self.log(f"Output: {result}")
                    messagebox.showinfo("Success", f"Compilation successful!\n\nOutput: {result}")
                else:
                    self.log("✗ Compilation failed!")
                    messagebox.showerror("Error", "Compilation failed! Check console for details.")
        
        threading.Thread(target=compile_thread, daemon=True).start()
    
    def compile_all(self):
        """Compile all projects"""
        projects_dir = Path("projects")
        if not projects_dir.exists():
            messagebox.showwarning("No Projects", "No projects found")
            return
        
        self.log("\n" + "="*60)
        self.log("Starting compilation of all projects")
        self.log("="*60)
        
        def compile_thread():
            projects = []
            for project in projects_dir.iterdir():
                if project.is_dir() and (project / "project.json").exists():
                    config = self.file_manager.get_project_config(project.name)
                    if config:
                        projects.append((project, config))
            
            if projects:
                results = self.compiler.compile_multiple_projects(projects)
                self.log(f"\n✓ Compiled {len(results)} out of {len(projects)} projects")
                messagebox.showinfo("Complete", f"Compiled {len(results)} out of {len(projects)} projects")
            else:
                self.log("No valid projects found")
        
        threading.Thread(target=compile_thread, daemon=True).start()
    
    def create_bundle(self):
        """Create a bundle of all compiled executables"""
        output_dir = Path("output")
        if not output_dir.exists() or not list(output_dir.glob("*.exe")):
            messagebox.showwarning("No Executables", "No compiled executables found")
            return
        
        bundle_name = filedialog.askstring("Bundle Name", "Enter bundle name:")
        if bundle_name:
            executables = list(output_dir.glob("*.exe"))
            result = self.compiler.create_bundle(executables, bundle_name)
            
            if result:
                self.log(f"✓ Bundle created: {result}")
                messagebox.showinfo("Success", f"Bundle created successfully!\n\n{result}")
            else:
                messagebox.showerror("Error", "Failed to create bundle")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = IDECompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# Made with Bob
