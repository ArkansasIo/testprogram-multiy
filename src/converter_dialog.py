"""
Language Converter Dialog
GUI for converting code between different programming languages
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from typing import Optional, Dict, List, Callable
from pathlib import Path
import threading

from language_converter import LanguageConverter, Language, CodeParser, CodeWriter, SyntaxRules
from project_hierarchy import ProjectHierarchy, HierarchyNode, NodeType, HierarchyManager


class LanguageConverterDialog:
    """Dialog for converting code between programming languages"""
    
    def __init__(self, parent, converter: LanguageConverter):
        self.parent = parent
        self.converter = converter
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Language Converter - Code Translation")
        self.dialog.geometry("1100x750")
        self.dialog.minsize(900, 600)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.source_content = ""
        self.result_content = ""
        
        self.setup_ui()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(1, weight=1)
        
        # Top controls
        controls = ttk.Frame(self.dialog, padding="10")
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)
        
        # Source language
        ttk.Label(controls, text="Source Language:", font=('Arial', 10)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.source_lang_var = tk.StringVar(value="python")
        self.source_combo = ttk.Combobox(controls, textvariable=self.source_lang_var,
                                         values=[l["value"] for l in self.converter.get_available_languages()],
                                         state="readonly", width=15)
        self.source_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Swap button
        ttk.Button(controls, text="⇄ Swap", command=self.swap_languages, 
                   width=8).grid(row=0, column=2, padx=5)
        
        # Target language
        ttk.Label(controls, text="Target Language:", font=('Arial', 10)).grid(
            row=0, column=3, sticky=tk.W, padx=(10, 5))
        self.target_lang_var = tk.StringVar(value="javascript")
        self.target_combo = ttk.Combobox(controls, textvariable=self.target_lang_var,
                                         values=[l["value"] for l in self.converter.get_available_languages()],
                                         state="readonly", width=15)
        self.target_combo.grid(row=0, column=4, sticky="ew", padx=(0, 10))
        
        # Action buttons
        btn_frame = ttk.Frame(controls)
        btn_frame.grid(row=0, column=5, padx=(10, 0))
        
        ttk.Button(btn_frame, text="Load File", command=self.load_file).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="Convert ▶", command=self.convert_code,
                   style="Accent.TButton").pack(side=tk.LEFT, padx=1)
        
        # Main content area
        content_frame = ttk.Frame(self.dialog, padding="10")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(2, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Source panel
        source_frame = ttk.LabelFrame(content_frame, text="Source Code", padding="5")
        source_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5))
        source_frame.columnconfigure(0, weight=1)
        source_frame.rowconfigure(1, weight=1)
        
        # Source info
        self.source_info_var = tk.StringVar(value="Character count: 0 | Lines: 0")
        ttk.Label(source_frame, textvariable=self.source_info_var, 
                 foreground="#888888").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.source_text = scrolledtext.ScrolledText(
            source_frame, wrap=tk.WORD, font=('Consolas', 11),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#ffffff",
            relief=tk.FLAT, borderwidth=0
        )
        self.source_text.grid(row=1, column=0, sticky="nsew")
        self.source_text.bind('<KeyRelease>', self.update_source_info)
        
        # Source actions
        source_actions = ttk.Frame(source_frame)
        source_actions.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(source_actions, text="Clear", 
                  command=lambda: self.source_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=1)
        ttk.Button(source_actions, text="Load from Editor", 
                  command=self.load_from_editor).pack(side=tk.LEFT, padx=1)
        ttk.Button(source_actions, text="Paste", 
                  command=lambda: self.source_text.insert(tk.INSERT, self.parent.clipboard_get())).pack(side=tk.LEFT, padx=1)
        
        # Arrow middle
        arrow_frame = ttk.Frame(content_frame)
        arrow_frame.grid(row=0, column=1, rowspan=2)
        
        ttk.Label(arrow_frame, text="▶", font=('Arial', 24, 'bold'),
                 foreground="#569cd6").pack(expand=True)
        
        ttk.Button(arrow_frame, text="Convert", command=self.convert_code,
                  width=10).pack(pady=10)
        
        ttk.Label(arrow_frame, text="◀", font=('Arial', 24, 'bold'),
                 foreground="#569cd6").pack(expand=True)
        
        # Target panel
        target_frame = ttk.LabelFrame(content_frame, text="Converted Code", padding="5")
        target_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 0))
        target_frame.columnconfigure(0, weight=1)
        target_frame.rowconfigure(1, weight=1)
        
        # Target info
        self.target_info_var = tk.StringVar(value="Character count: 0 | Lines: 0")
        ttk.Label(target_frame, textvariable=self.target_info_var,
                 foreground="#888888").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.target_text = scrolledtext.ScrolledText(
            target_frame, wrap=tk.WORD, font=('Consolas', 11),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#ffffff",
            relief=tk.FLAT, borderwidth=0
        )
        self.target_text.grid(row=1, column=0, sticky="nsew")
        self.target_text.config(state=tk.DISABLED)
        
        # Target actions
        target_actions = ttk.Frame(target_frame)
        target_actions.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(target_actions, text="Copy Result", 
                  command=self.copy_result).pack(side=tk.LEFT, padx=1)
        ttk.Button(target_actions, text="Save to File...", 
                  command=self.save_result).pack(side=tk.LEFT, padx=1)
        ttk.Button(target_actions, text="Send to Editor", 
                  command=self.send_to_editor).pack(side=tk.LEFT, padx=1)
        
        # Bottom - Language info
        info_frame = ttk.Frame(self.dialog, padding="5")
        info_frame.grid(row=2, column=0, sticky="ew")
        
        self.info_label = ttk.Label(info_frame, 
                                   text="Ready. Select languages and enter code to convert.",
                                   foreground="#888888")
        self.info_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate', length=200)
        
        # Keyboard shortcuts
        self.dialog.bind('<Control-Return>', lambda e: self.convert_code())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def update_source_info(self, event=None):
        """Update source code information"""
        content = self.source_text.get("1.0", "end-1c")
        chars = len(content)
        lines = content.count('\n') + 1 if content else 0
        self.source_info_var.set(f"Characters: {chars} | Lines: {lines}")
    
    def load_file(self):
        """Load a file as source code"""
        file_path = filedialog.askopenfilename(
            title="Select Source File",
            filetypes=[
                ("All Source Files", "*.py *.js *.ts *.c *.cpp *.java *.cs *.php *.rb *.go *.rs *.kt *.swift"),
                ("Python", "*.py"),
                ("JavaScript", "*.js"),
                ("TypeScript", "*.ts"),
                ("C/C++", "*.c *.cpp *.h *.hpp"),
                ("Java", "*.java"),
                ("C#", "*.cs"),
                ("PHP", "*.php"),
                ("Ruby", "*.rb"),
                ("Go", "*.go"),
                ("Rust", "*.rs"),
                ("Kotlin", "*.kt"),
                ("Swift", "*.swift"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                content = Path(file_path).read_text(encoding='utf-8', errors='replace')
                self.source_text.delete("1.0", tk.END)
                self.source_text.insert("1.0", content)
                
                # Auto-detect language
                ext = Path(file_path).suffix
                lang = Language.from_extension(ext)
                self.source_lang_var.set(lang.value)
                
                self.update_source_info()
                self.info_label.config(text=f"Loaded: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")
    
    def load_from_editor(self):
        """Load code from the main editor"""
        try:
            # Try to get from parent's tab manager
            if hasattr(self.parent, 'tab_manager'):
                editor = self.parent.tab_manager.get_current_editor()
                if editor:
                    content = editor.get_content()
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", content)
                    
                    if editor.file_path:
                        ext = Path(editor.file_path).suffix
                        lang = Language.from_extension(ext)
                        self.source_lang_var.set(lang.value)
                    
                    self.update_source_info()
                    self.info_label.config(text="Loaded from editor")
                    return
            
            messagebox.showinfo("No Editor", "No active editor found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load from editor: {e}")
    
    def swap_languages(self):
        """Swap source and target languages"""
        source = self.source_lang_var.get()
        target = self.target_lang_var.get()
        self.source_lang_var.set(target)
        self.target_lang_var.set(source)
        
        # Also swap content if result exists
        result_content = self.target_text.get("1.0", "end-1c") if self.target_text.get("1.0", "end-1c").strip() else ""
        source_content = self.source_text.get("1.0", "end-1c")
        
        if result_content and source_content:
            self.source_text.delete("1.0", tk.END)
            self.source_text.insert("1.0", result_content)
            self.target_text.config(state=tk.NORMAL)
            self.target_text.delete("1.0", tk.END)
            self.target_text.config(state=tk.DISABLED)
            self.update_source_info()
    
    def convert_code(self):
        """Perform the code conversion"""
        source = self.source_text.get("1.0", "end-1c")
        if not source.strip():
            messagebox.showwarning("No Code", "Please enter or load source code")
            return
        
        try:
            source_lang = Language.from_name(self.source_lang_var.get())
            target_lang = Language.from_name(self.target_lang_var.get())
            
            if source_lang == target_lang:
                messagebox.showinfo("Same Language", 
                                   "Source and target languages are the same.\n"
                                   "No conversion needed.")
                return
            
            self.info_label.config(text="Converting...")
            self.progress.pack(side=tk.RIGHT, padx=10)
            self.progress.start(10)
            self.dialog.update()
            
            # Perform conversion in thread
            def convert_thread():
                try:
                    result = self.converter.convert(source, source_lang, target_lang)
                    
                    self.dialog.after(0, lambda: self.display_result(result))
                    self.dialog.after(0, lambda: self.progress.stop())
                    self.dialog.after(0, lambda: self.progress.pack_forget())
                except Exception as e:
                    self.dialog.after(0, lambda: self.show_error(str(e)))
                    self.dialog.after(0, lambda: self.progress.stop())
                    self.dialog.after(0, lambda: self.progress.pack_forget())
            
            threading.Thread(target=convert_thread, daemon=True).start()
            
        except Exception as e:
            self.show_error(str(e))
    
    def display_result(self, result: str):
        """Display the conversion result"""
        self.target_text.config(state=tk.NORMAL)
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert("1.0", result)
        self.target_text.config(state=tk.DISABLED)
        
        chars = len(result)
        lines = result.count('\n') + 1 if result else 0
        self.target_info_var.set(f"Characters: {chars} | Lines: {lines}")
        
        self.info_label.config(text=f"✓ Conversion complete! Generated {lines} lines of code.")
    
    def show_error(self, error: str):
        """Show an error message"""
        self.info_label.config(text=f"✗ Error: {error}")
        messagebox.showerror("Conversion Error", 
                            f"Failed to convert code:\n\n{error}")
    
    def copy_result(self):
        """Copy result to clipboard"""
        result = self.target_text.get("1.0", "end-1c")
        if result.strip():
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(result)
            self.info_label.config(text="✓ Result copied to clipboard")
        else:
            messagebox.showinfo("No Result", "No converted code to copy")
    
    def save_result(self):
        """Save result to a file"""
        result = self.target_text.get("1.0", "end-1c")
        if not result.strip():
            messagebox.showinfo("No Result", "No converted code to save")
            return
        
        target_lang = Language.from_name(self.target_lang_var.get())
        ext = target_lang.extensions[0] if target_lang.extensions else ".txt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Converted Code",
            defaultextension=ext,
            filetypes=[
                ("Source files", f"*{ext}"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                Path(file_path).write_text(result, encoding='utf-8')
                self.info_label.config(text=f"✓ Saved to {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def send_to_editor(self):
        """Send result to main editor"""
        result = self.target_text.get("1.0", "end-1c")
        if not result.strip():
            messagebox.showinfo("No Result", "No converted code to send")
            return
        
        try:
            if hasattr(self.parent, 'tab_manager'):
                editor = self.parent.tab_manager.get_current_editor()
                if editor:
                    editor.set_content(result)
                    self.info_label.config(text="✓ Sent to editor")
                    return
            
            messagebox.showinfo("No Editor", "No active editor found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send to editor: {e}")


class HierarchyDialog:
    """Dialog for managing project hierarchy with categories, modules, and IDs"""
    
    def __init__(self, parent, hierarchy_manager: HierarchyManager, project_name: str):
        self.parent = parent
        self.hierarchy_manager = hierarchy_manager
        self.project_name = project_name
        
        # Get or create hierarchy
        self.hierarchy = hierarchy_manager.get_hierarchy(project_name)
        if not self.hierarchy:
            self.hierarchy = hierarchy_manager.create_hierarchy(project_name)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Project Hierarchy - {project_name}")
        self.dialog.geometry("900x650")
        self.dialog.minsize(700, 500)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.refresh_tree()
        
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Tree view
        tree_frame = ttk.LabelFrame(main_frame, text="Hierarchy Tree", padding="5")
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Tree with scrollbar
        tree_container = ttk.Frame(tree_frame)
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(tree_container, columns=("id", "number", "type"), 
                                 show="tree", height=20)
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Tree buttons
        tree_buttons = ttk.Frame(tree_frame)
        tree_buttons.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(tree_buttons, text="Expand All", command=self.expand_all).pack(side=tk.LEFT, padx=1)
        ttk.Button(tree_buttons, text="Collapse All", command=self.collapse_all).pack(side=tk.LEFT, padx=1)
        ttk.Button(tree_buttons, text="Refresh", command=self.refresh_tree).pack(side=tk.RIGHT, padx=1)
        
        # Right panel - Node details and actions
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        
        # Node details
        details_frame = ttk.LabelFrame(right_frame, text="Node Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.node_name_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.node_name_var, width=30).grid(
            row=0, column=1, sticky="ew", padx=(5, 0))
        
        ttk.Label(details_frame, text="Type:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.node_type_var = tk.StringVar(value="file")
        type_combo = ttk.Combobox(details_frame, textvariable=self.node_type_var,
                                 values=[t.value for t in NodeType],
                                 state="readonly", width=20)
        type_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        ttk.Label(details_frame, text="Description:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.node_desc_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.node_desc_var, width=30).grid(
            row=2, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))
        
        ttk.Label(details_frame, text="ID:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.node_id_var = tk.StringVar(value="(not selected)")
        ttk.Label(details_frame, textvariable=self.node_id_var, foreground="#888888").grid(
            row=3, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        ttk.Label(details_frame, text="Number:").grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        self.node_number_var = tk.StringVar(value="-")
        ttk.Label(details_frame, textvariable=self.node_number_var).grid(
            row=4, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        ttk.Label(details_frame, text="Path:").grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        self.node_path_var = tk.StringVar(value="-")
        ttk.Label(details_frame, textvariable=self.node_path_var, foreground="#569cd6").grid(
            row=5, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        details_frame.columnconfigure(1, weight=1)
        
        # Actions
        actions_frame = ttk.LabelFrame(right_frame, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add buttons
        add_frame = ttk.Frame(actions_frame)
        add_frame.pack(fill=tk.X, pady=2)
        ttk.Label(add_frame, text="Add:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Button(add_frame, text="Category", command=lambda: self.add_node("category"), 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(add_frame, text="Module", command=lambda: self.add_node("module"), 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(add_frame, text="Folder", command=lambda: self.add_node("folder"), 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(add_frame, text="File", command=lambda: self.add_node("file"), 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(add_frame, text="Part", command=lambda: self.add_node("part"), 
                  width=10).pack(side=tk.LEFT, padx=2)
        
        sub_frame = ttk.Frame(actions_frame)
        sub_frame.pack(fill=tk.X, pady=2)
        ttk.Label(sub_frame, text="Sub:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Button(sub_frame, text="Subcategory", command=lambda: self.add_node("subcategory"), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(sub_frame, text="Submodule", command=lambda: self.add_node("submodule"), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(sub_frame, text="Subfolder", command=lambda: self.add_node("subfolder"), 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(sub_frame, text="Subpart", command=lambda: self.add_node("subpart"), 
                  width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(actions_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Modify buttons
        modify_frame = ttk.Frame(actions_frame)
        modify_frame.pack(fill=tk.X, pady=2)
        ttk.Button(modify_frame, text="Update Node", command=self.update_node, 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(modify_frame, text="Delete Node", command=self.delete_node, 
                  width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(modify_frame, text="Move Up", command=self.move_up, 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(modify_frame, text="Move Down", command=self.move_down, 
                  width=10).pack(side=tk.LEFT, padx=2)
        
        # Search
        search_frame = ttk.LabelFrame(right_frame, text="Search", padding="5")
        search_frame.pack(fill=tk.X)
        
        search_input = ttk.Frame(search_frame)
        search_input.pack(fill=tk.X)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_input, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<Return>', lambda e: self.search_nodes())
        
        ttk.Button(search_input, text="Search", command=self.search_nodes).pack(side=tk.LEFT, padx=1)
        ttk.Button(search_input, text="Clear", command=self.refresh_tree).pack(side=tk.LEFT, padx=1)
        
        # Search results
        self.search_results_var = tk.StringVar(value="")
        ttk.Label(search_frame, textvariable=self.search_results_var, 
                 foreground="#888888").pack(anchor=tk.W, pady=(5, 0))
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
    
    def refresh_tree(self, search_results=None):
        """Refresh the tree view"""
        self.tree.delete(*self.tree.get_children())
        
        if search_results:
            nodes = search_results
        else:
            nodes = [self.hierarchy.root]
        
        def add_nodes(parent_node, parent_item=""):
            for child in parent_node.children:
                # Build display text
                display = f"[{child.get_path_numbers()}] {child.node_type.value.upper()}: {child.name}"
                
                # Insert into tree
                item = self.tree.insert(parent_item, tk.END, 
                                       text=display,
                                       values=(child.id, child.number, child.node_type.value))
                
                # Add children recursively
                add_nodes(child, item)
                
                if not search_results:
                    self.tree.item(item, open=True)
        
        add_nodes(self.hierarchy.root)
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                node_id = values[0]
                node = self.hierarchy.get_node(node_id)
                if node:
                    self.node_name_var.set(node.name)
                    self.node_type_var.set(node.node_type.value)
                    self.node_desc_var.set(node.description)
                    self.node_id_var.set(node.id)
                    self.node_number_var.set(f"[{node.get_path_numbers()}] #{node.number}")
                    self.node_path_var.set(node.get_path_names())
    
    def on_tree_double_click(self, event):
        """Handle double click on tree"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Toggle expand/collapse
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)
    
    def add_node(self, node_type_str: str):
        """Add a new node"""
        selection = self.tree.selection()
        parent = self.hierarchy.root
        
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values:
                parent_id = values[0]
                parent = self.hierarchy.get_node(parent_id)
                if parent is None:
                    parent = self.hierarchy.root
        
        # Get name
        name = tk.simpledialog.askstring("Add Node", 
                                         f"Enter name for new {node_type_str}:",
                                         parent=self.dialog)
        if not name:
            return
        
        try:
            node_type = NodeType(node_type_str)
            
            if node_type == NodeType.CATEGORY:
                if parent == self.hierarchy.root:
                    self.hierarchy.add_category(name)
                else:
                    self.hierarchy.add_subcategory(parent, name)
            elif node_type == NodeType.SUBCATEGORY:
                self.hierarchy.add_subcategory(parent, name)
            elif node_type == NodeType.MODULE:
                self.hierarchy.add_module(parent, name)
            elif node_type == NodeType.SUBMODULE:
                self.hierarchy.add_submodule(parent, name)
            elif node_type == NodeType.FOLDER:
                if parent.node_type in [NodeType.CATEGORY, NodeType.SUBCATEGORY, NodeType.FOLDER]:
                    self.hierarchy.add_folder(parent, name)
                else:
                    self.hierarchy.add_subfolder(parent, name)
            elif node_type == NodeType.SUBFOLDER:
                self.hierarchy.add_subfolder(parent, name)
            elif node_type == NodeType.FILE:
                self.hierarchy.add_file(parent, name)
            elif node_type == NodeType.PART:
                self.hierarchy.add_part(parent, name)
            elif node_type == NodeType.SUBPART:
                self.hierarchy.add_subpart(parent, name)
            else:
                self.hierarchy.add_folder(parent, name)
            
            self.hierarchy.renumber_all()
            self.refresh_tree()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not add node: {e}")
    
    def update_node(self):
        """Update selected node"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a node")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        
        node_id = values[0]
        node = self.hierarchy.get_node(node_id)
        if node:
            node.name = self.node_name_var.get()
            node.description = self.node_desc_var.get()
            # Can't change type after creation for safety
            self.refresh_tree()
    
    def delete_node(self):
        """Delete selected node"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a node")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        
        node_id = values[0]
        node = self.hierarchy.get_node(node_id)
        if node and node != self.hierarchy.root:
            name = node.name
            if messagebox.askyesno("Delete Node", 
                                  f"Delete '{name}' and all its children?"):
                self.hierarchy.remove_node(node_id)
                self.refresh_tree()
                self.clear_details()
    
    def move_up(self):
        """Move selected node up"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        
        node_id = values[0]
        node = self.hierarchy.get_node(node_id)
        if node and node.parent_id:
            parent = self.hierarchy.get_node(node.parent_id)
            if parent:
                idx = parent.children.index(node)
                if idx > 0:
                    parent.children[idx], parent.children[idx - 1] = parent.children[idx - 1], parent.children[idx]
                    self.hierarchy.renumber_all()
                    self.refresh_tree()
    
    def move_down(self):
        """Move selected node down"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        if not values:
            return
        
        node_id = values[0]
        node = self.hierarchy.get_node(node_id)
        if node and node.parent_id:
            parent = self.hierarchy.get_node(node.parent_id)
            if parent:
                idx = parent.children.index(node)
                if idx < len(parent.children) - 1:
                    parent.children[idx], parent.children[idx + 1] = parent.children[idx + 1], parent.children[idx]
                    self.hierarchy.renumber_all()
                    self.refresh_tree()
    
    def search_nodes(self):
        """Search for nodes"""
        query = self.search_var.get().strip()
        if not query:
            self.refresh_tree()
            return
        
        results = self.hierarchy.search_nodes(query)
        self.search_results_var.set(f"Found {len(results)} results")
        
        if results:
            self.refresh_tree(search_results=results)
        else:
            self.refresh_tree()
    
    def expand_all(self):
        """Expand all tree nodes"""
        for item in self.tree.get_children():
            self._expand_recursive(item)
    
    def _expand_recursive(self, item):
        """Recursively expand tree items"""
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self._expand_recursive(child)
    
    def collapse_all(self):
        """Collapse all tree nodes"""
        for item in self.tree.get_children():
            self.tree.item(item, open=False)
    
    def clear_details(self):
        """Clear node details"""
        self.node_name_var.set("")
        self.node_type_var.set("file")
        self.node_desc_var.set("")
        self.node_id_var.set("(not selected)")
        self.node_number_var.set("-")
        self.node_path_var.set("-")


# Made with Bob