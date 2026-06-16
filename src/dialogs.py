"""
Dialog Modules
Settings Dialog, Find/Replace Dialog, and other IDE dialogs
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font as tkfont
from typing import Optional, Dict, Any, Callable, List
from pathlib import Path


class SettingsDialog:
    """Full-featured settings dialog with categorized tabs"""
    
    def __init__(self, parent, settings_manager, callback: Optional[Callable] = None):
        self.parent = parent
        self.settings = settings_manager
        self.callback = callback
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("IDE Settings")
        self.dialog.geometry("700x550")
        self.dialog.minsize(600, 400)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_settings()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the settings dialog UI"""
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Create tabs
        self.general_tab = self.create_general_tab()
        self.editor_tab = self.create_editor_tab()
        self.build_tab = self.create_build_tab()
        self.project_tab = self.create_project_tab()
        self.keybindings_tab = self.create_keybindings_tab()
        
        self.notebook.add(self.general_tab, text="  General  ")
        self.notebook.add(self.editor_tab, text="  Editor  ")
        self.notebook.add(self.build_tab, text="  Build  ")
        self.notebook.add(self.project_tab, text="  Project  ")
        self.notebook.add(self.keybindings_tab, text="  Keybindings  ")
        
        # Bottom buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_frame, text="OK", command=self.ok_settings).pack(side=tk.RIGHT, padx=2)
    
    def create_general_tab(self):
        """Create the general settings tab"""
        frame = ttk.Frame(self.notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(frame, text="General Settings", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        row += 1
        ttk.Label(frame, text="Language:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.language_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(frame, textvariable=self.language_var, values=["en", "es", "fr", "de", "ja", "zh", "ru"], width=20)
        lang_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        self.auto_save_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Auto-Save Files", variable=self.auto_save_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        ttk.Label(frame, text="Auto-Save Interval (seconds):").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.auto_save_interval_var = tk.IntVar(value=30)
        ttk.Spinbox(frame, from_=5, to=300, textvariable=self.auto_save_interval_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        self.confirm_exit_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Confirm on Exit", variable=self.confirm_exit_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.restore_session_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Restore Last Session on Startup", variable=self.restore_session_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.check_updates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Check for Updates", variable=self.check_updates_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        ttk.Label(frame, text="Recent Projects Limit:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.recent_projects_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=50, textvariable=self.recent_projects_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Recent Files Limit:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.recent_files_var = tk.IntVar(value=10)
        ttk.Spinbox(frame, from_=1, to=50, textvariable=self.recent_files_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Separator
        row += 1
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        row += 1
        ttk.Label(frame, text="Window State:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.window_state_var = tk.StringVar(value="normal")
        state_combo = ttk.Combobox(frame, textvariable=self.window_state_var, 
                                   values=["normal", "maximized", "fullscreen"], width=15)
        state_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Add scrollbar capability
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Replace frame content with scrollable version if many items
        # For now, return the normal frame
        return frame
    
    def create_editor_tab(self):
        """Create the editor settings tab"""
        frame = ttk.Frame(self.notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(frame, text="Editor Settings", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        row += 1
        ttk.Label(frame, text="Font Family:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.font_family_var = tk.StringVar(value="Consolas")
        fonts = ["Consolas", "Courier New", "Monaco", "Menlo", "DejaVu Sans Mono", 
                 "Fira Code", "Source Code Pro", "JetBrains Mono"]
        font_combo = ttk.Combobox(frame, textvariable=self.font_family_var, values=fonts, width=20)
        font_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Font Size:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.font_size_var = tk.IntVar(value=11)
        ttk.Spinbox(frame, from_=8, to=72, textvariable=self.font_size_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Tab Size:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.tab_size_var = tk.IntVar(value=4)
        ttk.Spinbox(frame, from_=1, to=8, textvariable=self.tab_size_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        self.use_spaces_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Use Spaces Instead of Tabs", variable=self.use_spaces_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.wrap_text_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Wrap Text", variable=self.wrap_text_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.show_line_numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Show Line Numbers", variable=self.show_line_numbers_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.highlight_line_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Highlight Current Line", variable=self.highlight_line_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.auto_indent_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-Indent", variable=self.auto_indent_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.auto_close_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-Close Brackets & Quotes", variable=self.auto_close_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.match_brackets_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Match Brackets", variable=self.match_brackets_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.syntax_highlighting_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Syntax Highlighting", variable=self.syntax_highlighting_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        ttk.Label(frame, text="Theme:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.theme_var = tk.StringVar(value="dark")
        theme_combo = ttk.Combobox(frame, textvariable=self.theme_var, 
                                   values=["dark", "light", "high-contrast"], width=15)
        theme_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        return frame
    
    def create_build_tab(self):
        """Create the build settings tab"""
        frame = ttk.Frame(self.notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(frame, text="Build Settings", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        row += 1
        self.default_onefile_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Default to Single File EXE", variable=self.default_onefile_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.default_console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Default to Showing Console", variable=self.default_console_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.clean_build_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Clean Build (Remove Cache)", variable=self.clean_build_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.auto_build_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Auto-Build on Save", variable=self.auto_build_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        ttk.Label(frame, text="Compression Level:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.compression_var = tk.StringVar(value="normal")
        comp_combo = ttk.Combobox(frame, textvariable=self.compression_var,
                                  values=["fast", "normal", "maximum"], width=15)
        comp_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Optimization:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.optimization_var = tk.StringVar(value="balanced")
        opt_combo = ttk.Combobox(frame, textvariable=self.optimization_var,
                                values=["none", "basic", "balanced", "aggressive"], width=15)
        opt_combo.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Output Directory:").grid(row=row, column=0, sticky=tk.W, pady=2)
        output_frame = ttk.Frame(frame)
        output_frame.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        self.output_dir_var = tk.StringVar(value="output")
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).pack(side=tk.LEFT)
        
        row += 1
        self.parallel_builds_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Parallel Builds", variable=self.parallel_builds_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        ttk.Label(frame, text="Max Parallel Builds:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.max_parallel_var = tk.IntVar(value=4)
        ttk.Spinbox(frame, from_=1, to=16, textvariable=self.max_parallel_var, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        return frame
    
    def create_project_tab(self):
        """Create the project defaults tab"""
        frame = ttk.Frame(self.notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(frame, text="Project Defaults", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        row += 1
        ttk.Label(frame, text="Default Entry Point:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.entry_point_var = tk.StringVar(value="main.py")
        ttk.Entry(frame, textvariable=self.entry_point_var, width=25).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Default Output Name:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.output_name_var = tk.StringVar(value="{project}.exe")
        ttk.Entry(frame, textvariable=self.output_name_var, width=25).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        ttk.Label(frame, text="Default Version:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.default_version_var = tk.StringVar(value="1.0.0")
        ttk.Entry(frame, textvariable=self.default_version_var, width=15).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        row += 1
        self.create_resources_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Create Resources Directory", variable=self.create_resources_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.create_libs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Create Libraries Directory", variable=self.create_libs_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.create_tests_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Create Tests Directory", variable=self.create_tests_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.create_docs_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Create Docs Directory", variable=self.create_docs_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.add_gitignore_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Add .gitignore File", variable=self.add_gitignore_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        row += 1
        self.add_readme_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Add README.md File", variable=self.add_readme_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        return frame
    
    def create_keybindings_tab(self):
        """Create the keybindings settings tab"""
        frame = ttk.Frame(self.notebook, padding="15")
        frame.columnconfigure(1, weight=1)
        
        row = 0
        ttk.Label(frame, text="Keyboard Shortcuts", font=('Arial', 12, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        row += 1
        ttk.Label(frame, text="IDE Keyboard Shortcuts:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        shortcuts = [
            ("Ctrl+N", "New Project"),
            ("Ctrl+O", "Open Project"),
            ("Ctrl+S", "Save Current File"),
            ("Ctrl+Shift+S", "Save All Files"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
            ("Ctrl+X", "Cut"),
            ("Ctrl+C", "Copy"),
            ("Ctrl+V", "Paste"),
            ("Ctrl+A", "Select All"),
            ("Ctrl+F", "Find"),
            ("Ctrl+H", "Find & Replace"),
            ("Ctrl+D", "Duplicate Line"),
            ("Ctrl+L", "Go to Line"),
            ("Ctrl+/", "Toggle Comment"),
            ("Ctrl+]", "Indent"),
            ("Ctrl+[", "Unindent"),
            ("Ctrl+B", "Build/Compile"),
            ("Ctrl+Shift+B", "Build All"),
            ("Ctrl+`", "Toggle Console"),
            ("Ctrl+P", "Quick Open File"),
            ("Ctrl+Shift+P", "Command Palette"),
            ("Ctrl+W", "Close Tab"),
            ("Ctrl+Tab", "Next Tab"),
            ("Ctrl+Shift+Tab", "Previous Tab"),
            ("F5", "Run"),
            ("F12", "Build Current"),
        ]
        
        # Create a treeview for shortcuts
        columns = ("shortcut", "action")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
        tree.heading("shortcut", text="Keybinding")
        tree.heading("action", text="Action")
        tree.column("shortcut", width=150)
        tree.column("action", width=300)
        
        for shortcut, action in shortcuts:
            tree.insert("", tk.END, values=(shortcut, action))
        
        tree.grid(row=row, column=0, columnspan=2, sticky="nsew", pady=2)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.grid(row=row, column=2, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        
        frame.rowconfigure(row, weight=1)
        
        row += 1
        ttk.Label(frame, text="\nNote: Keybindings are predefined and can be customized in the settings file.",
                  foreground="#888888").grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        return frame
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = tk.filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def load_settings(self):
        """Load current settings into dialog fields"""
        s = self.settings.settings
        
        # General
        self.language_var.set(s.general.language)
        self.auto_save_var.set(s.general.auto_save)
        self.auto_save_interval_var.set(s.general.auto_save_interval)
        self.confirm_exit_var.set(s.general.confirm_exit)
        self.restore_session_var.set(s.general.restore_last_session)
        self.check_updates_var.set(s.general.check_updates)
        self.recent_projects_var.set(s.general.recent_projects_limit)
        self.recent_files_var.set(s.general.recent_files_limit)
        self.window_state_var.set(s.general.window_state)
        
        # Editor
        self.font_family_var.set(s.editor.font_family)
        self.font_size_var.set(s.editor.font_size)
        self.tab_size_var.set(s.editor.tab_size)
        self.use_spaces_var.set(s.editor.use_spaces)
        self.wrap_text_var.set(s.editor.wrap_text)
        self.show_line_numbers_var.set(s.editor.show_line_numbers)
        self.highlight_line_var.set(s.editor.highlight_current_line)
        self.auto_indent_var.set(s.editor.auto_indent)
        self.auto_close_var.set(s.editor.auto_close_brackets)
        self.match_brackets_var.set(s.editor.match_brackets)
        self.syntax_highlighting_var.set(s.editor.syntax_highlighting)
        self.theme_var.set(s.editor.theme)
        
        # Build
        self.default_onefile_var.set(s.build.default_onefile)
        self.default_console_var.set(s.build.default_console)
        self.clean_build_var.set(s.build.clean_build)
        self.auto_build_var.set(s.build.auto_build_on_save)
        self.compression_var.set(s.build.compression_level)
        self.optimization_var.set(s.build.optimization_level)
        self.output_dir_var.set(s.build.output_directory)
        self.parallel_builds_var.set(s.build.parallel_builds)
        self.max_parallel_var.set(s.build.max_parallel_builds)
        
        # Project
        self.entry_point_var.set(s.project.default_entry_point)
        self.output_name_var.set(s.project.default_output_name)
        self.default_version_var.set(s.project.default_version)
        self.create_resources_var.set(s.project.create_resources_dir)
        self.create_libs_var.set(s.project.create_libs_dir)
        self.create_tests_var.set(s.project.create_tests_dir)
        self.create_docs_var.set(s.project.create_docs_dir)
        self.add_gitignore_var.set(s.project.add_gitignore)
        self.add_readme_var.set(s.project.add_readme)
    
    def apply_settings(self):
        """Apply current dialog values to settings"""
        s = self.settings.settings
        
        # General
        s.general.language = self.language_var.get()
        s.general.auto_save = self.auto_save_var.get()
        s.general.auto_save_interval = self.auto_save_interval_var.get()
        s.general.confirm_exit = self.confirm_exit_var.get()
        s.general.restore_last_session = self.restore_session_var.get()
        s.general.check_updates = self.check_updates_var.get()
        s.general.recent_projects_limit = self.recent_projects_var.get()
        s.general.recent_files_limit = self.recent_files_var.get()
        s.general.window_state = self.window_state_var.get()
        
        # Editor
        s.editor.font_family = self.font_family_var.get()
        s.editor.font_size = self.font_size_var.get()
        s.editor.tab_size = self.tab_size_var.get()
        s.editor.use_spaces = self.use_spaces_var.get()
        s.editor.wrap_text = self.wrap_text_var.get()
        s.editor.show_line_numbers = self.show_line_numbers_var.get()
        s.editor.highlight_current_line = self.highlight_line_var.get()
        s.editor.auto_indent = self.auto_indent_var.get()
        s.editor.auto_close_brackets = self.auto_close_var.get()
        s.editor.match_brackets = self.match_brackets_var.get()
        s.editor.syntax_highlighting = self.syntax_highlighting_var.get()
        s.editor.theme = self.theme_var.get()
        
        # Build
        s.build.default_onefile = self.default_onefile_var.get()
        s.build.default_console = self.default_console_var.get()
        s.build.clean_build = self.clean_build_var.get()
        s.build.auto_build_on_save = self.auto_build_var.get()
        s.build.compression_level = self.compression_var.get()
        s.build.optimization_level = self.optimization_var.get()
        s.build.output_directory = self.output_dir_var.get()
        s.build.parallel_builds = self.parallel_builds_var.get()
        s.build.max_parallel_builds = self.max_parallel_var.get()
        
        # Project
        s.project.default_entry_point = self.entry_point_var.get()
        s.project.default_output_name = self.output_name_var.get()
        s.project.default_version = self.default_version_var.get()
        s.project.create_resources_dir = self.create_resources_var.get()
        s.project.create_libs_dir = self.create_libs_var.get()
        s.project.create_tests_dir = self.create_tests_var.get()
        s.project.create_docs_dir = self.create_docs_var.get()
        s.project.add_gitignore = self.add_gitignore_var.get()
        s.project.add_readme = self.add_readme_var.get()
        
        # Save
        self.settings.save()
        
        if self.callback:
            self.callback()
    
    def ok_settings(self):
        """Apply and close"""
        self.apply_settings()
        self.dialog.destroy()
    
    def reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to default values?"):
            self.settings.reset_to_defaults()
            self.load_settings()


class FindReplaceDialog:
    """Find and Replace dialog for the code editor"""
    
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Find & Replace")
        self.dialog.geometry("450x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Position near the editor
        self.dialog.update_idletasks()
        x = parent.winfo_x() + 100
        y = parent.winfo_y() + 100
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the find/replace dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Find
        ttk.Label(main_frame, text="Find:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.find_var = tk.StringVar()
        self.find_entry = ttk.Entry(main_frame, textvariable=self.find_var, width=40)
        self.find_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        self.find_entry.focus()
        self.find_entry.bind('<KeyRelease>', lambda e: self.find_all())
        self.find_entry.bind('<Return>', lambda e: self.find_next())
        
        # Replace
        ttk.Label(main_frame, text="Replace:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.replace_var = tk.StringVar()
        self.replace_entry = ttk.Entry(main_frame, textvariable=self.replace_var, width=40)
        self.replace_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        self.replace_entry.bind('<Return>', lambda e: self.replace_next())
        
        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Case Sensitive", variable=self.case_sensitive_var,
                        command=self.find_all).pack(side=tk.LEFT, padx=5)
        
        self.whole_word_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Whole Word", variable=self.whole_word_var,
                        command=self.find_all).pack(side=tk.LEFT, padx=5)
        
        self.regex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Regex", variable=self.regex_var,
                        command=self.find_all).pack(side=tk.LEFT, padx=5)
        
        # Match count label
        self.match_count_var = tk.StringVar(value="")
        ttk.Label(options_frame, textvariable=self.match_count_var).pack(side=tk.RIGHT, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Find All", command=self.find_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Find Next", command=self.find_next).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Find Previous", command=self.find_previous).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Replace", command=self.replace_next).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Replace All", command=self.replace_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
        
        main_frame.columnconfigure(1, weight=1)
    
    def find_all(self):
        """Find all occurrences"""
        search_term = self.find_var.get()
        if not search_term:
            self.match_count_var.set("")
            return
        
        count = self.editor.find_all(search_term, self.case_sensitive_var.get())
        self.match_count_var.set(f"{count} matches")
        
        if count > 0:
            self.editor.text.see("1.0")
    
    def find_next(self):
        """Find next occurrence"""
        search_term = self.find_var.get()
        if not search_term:
            return
        
        cursor = self.editor.text.index(tk.INSERT)
        pos = self.editor.find_text(search_term, cursor, self.case_sensitive_var.get())
        
        # If not found from cursor, wrap to beginning
        if not pos:
            pos = self.editor.find_text(search_term, "1.0", self.case_sensitive_var.get())
    
    def find_previous(self):
        """Find previous occurrence"""
        search_term = self.find_var.get()
        if not search_term:
            return
        
        # Clear highlights and search from cursor backwards
        cursor = self.editor.text.index(tk.INSERT)
        cursor_line = int(cursor.split('.')[0])
        
        if cursor_line > 1:
            prev_line = f"{cursor_line - 1}.0"
            pos = self.editor.text.search(
                search_term, prev_line, "1.0",
                nocase=not self.case_sensitive_var.get(),
                backwards=True
            )
            
            if pos:
                end_pos = f"{pos} + {len(search_term)}c"
                self.editor.text.tag_remove("find_match", "1.0", "end")
                self.editor.text.tag_add("find_match", pos, end_pos)
                self.editor.text.see(pos)
                self.editor.text.mark_set(tk.INSERT, pos)
    
    def replace_next(self):
        """Replace next occurrence"""
        search_term = self.find_var.get()
        replace_term = self.replace_var.get()
        
        if not search_term:
            return
        
        # Find current match
        sel_ranges = self.editor.text.tag_ranges("find_match")
        if sel_ranges:
            # Replace the first match
            pos = str(sel_ranges[0])
            end_pos = f"{pos} + {len(search_term)}c"
            
            content = self.editor.text.get(pos, end_pos)
            if content == search_term or (not self.case_sensitive_var.get() and 
                                          content.lower() == search_term.lower()):
                self.editor.text.delete(pos, end_pos)
                self.editor.text.insert(pos, replace_term)
                
                # Clear and re-find
                self.find_all()
        else:
            self.find_next()
    
    def replace_all(self):
        """Replace all occurrences"""
        search_term = self.find_var.get()
        replace_term = self.replace_var.get()
        
        if not search_term:
            return
        
        count = self.editor.replace_text(search_term, replace_term, self.case_sensitive_var.get())
        self.match_count_var.set(f"Replaced {count} occurrences")
        messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).")


class GoToLineDialog:
    """Go to line number dialog"""
    
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Go to Line")
        self.dialog.geometry("300x120")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        self.dialog.update_idletasks()
        x = parent.winfo_x() + 150
        y = parent.winfo_y() + 150
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Line Number:").pack(anchor=tk.W, pady=(0, 5))
        
        self.line_var = tk.IntVar(value=1)
        spinbox = ttk.Spinbox(main_frame, from_=1, to=999999, textvariable=self.line_var, width=15)
        spinbox.pack(pady=5)
        spinbox.focus()
        spinbox.bind('<Return>', lambda e: self.go_to_line())
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Go", command=self.go_to_line).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
    
    def go_to_line(self):
        """Go to the specified line"""
        line_num = self.line_var.get()
        if line_num > 0:
            self.editor.text.mark_set(tk.INSERT, f"{line_num}.0")
            self.editor.text.see(f"{line_num}.0")
            self.editor.highlight_current_line()
            self.dialog.destroy()


class NewProjectDialog:
    """Enhanced new project dialog with options"""
    
    def __init__(self, parent, callback: Callable):
        self.parent = parent
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("New Project")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 350) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Project name
        ttk.Label(main_frame, text="Project Name:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=35)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 5))
        self.name_entry.focus()
        
        # Entry point
        ttk.Label(main_frame, text="Entry Point:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_var = tk.StringVar(value="main.py")
        ttk.Entry(main_frame, textvariable=self.entry_var, width=35).grid(
            row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Version
        ttk.Label(main_frame, text="Version:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.version_var = tk.StringVar(value="1.0.0")
        ttk.Entry(main_frame, textvariable=self.version_var, width=15).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Options
        ttk.Label(main_frame, text="Project Options:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        self.create_resources_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Create Resources Directory", 
                        variable=self.create_resources_var).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.create_libs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Create Libraries Directory", 
                        variable=self.create_libs_var).grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.add_gitignore_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Add .gitignore File", 
                        variable=self.add_gitignore_var).grid(
            row=7, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.add_readme_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Add README.md File", 
                        variable=self.add_readme_var).grid(
            row=8, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_frame, text="Create Project", command=self.create_project).pack(side=tk.RIGHT, padx=2)
        
        main_frame.columnconfigure(1, weight=1)
    
    def create_project(self):
        """Create the project with specified options"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Invalid Name", "Please enter a project name")
            return
        
        options = {
            "name": name,
            "entry_point": self.entry_var.get().strip() or "main.py",
            "version": self.version_var.get().strip() or "1.0.0",
            "create_resources": self.create_resources_var.get(),
            "create_libs": self.create_libs_var.get(),
            "add_gitignore": self.add_gitignore_var.get(),
            "add_readme": self.add_readme_var.get()
        }
        
        self.callback(options)
        self.dialog.destroy()


# Made with Bob