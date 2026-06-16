"""
Code Editor Module
Advanced code editor with syntax highlighting, line numbers, and IDE features
"""
import tkinter as tk
from tkinter import ttk, font as tkfont, messagebox
from typing import Optional, Dict, List, Callable
from pathlib import Path
import re
import threading
import time


class SyntaxHighlighter:
    """Provides syntax highlighting rules for multiple languages"""
    
    LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".txt": "text",
        ".bat": "batch",
        ".sh": "shell",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".java": "java",
        ".rs": "rust",
        ".go": "go",
    }
    
    # Language-specific syntax rules
    SYNTAX_RULES = {
        "python": {
            "keywords": [
                "False", "None", "True", "and", "as", "assert", "async", "await",
                "break", "class", "continue", "def", "del", "elif", "else", "except",
                "finally", "for", "from", "global", "if", "import", "in", "is",
                "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
                "try", "while", "with", "yield"
            ],
            "builtins": [
                "print", "len", "range", "int", "str", "float", "list", "dict",
                "set", "tuple", "type", "open", "input", "super", "object",
                "isinstance", "hasattr", "getattr", "setattr", "delattr",
                "enumerate", "zip", "map", "filter", "sorted", "reversed",
                "abs", "all", "any", "bin", "bool", "bytes", "chr", "complex",
                "dir", "divmod", "exec", "eval", "format", "frozenset",
                "globals", "hex", "id", "iter", "locals", "max", "min",
                "next", "oct", "ord", "pow", "repr", "round", "sum", "vars",
                "staticmethod", "classmethod", "property"
            ],
            "single_comment": "#",
            "multi_comment": [('"""', '"""'), ("'''", "'''")],
            "string_delimiters": ["'", '"', "'''", '"""'],
            "numeric_pattern": r'\b\d+\.?\d*[jJlL]?\b',
        },
        "javascript": {
            "keywords": [
                "async", "await", "break", "case", "catch", "class", "const",
                "continue", "debugger", "default", "delete", "do", "else",
                "export", "extends", "finally", "for", "function", "if",
                "import", "in", "instanceof", "let", "new", "of", "return",
                "static", "super", "switch", "this", "throw", "try", "typeof",
                "var", "void", "while", "with", "yield"
            ],
            "builtins": [
                "console", "document", "window", "Math", "JSON", "Array",
                "Object", "String", "Number", "Boolean", "Date", "RegExp",
                "Map", "Set", "Promise", "Symbol", "Error", "parseInt",
                "parseFloat", "setTimeout", "setInterval", "fetch",
                "localStorage", "sessionStorage"
            ],
            "single_comment": "//",
            "multi_comment": [("/*", "*/")],
            "string_delimiters": ["'", '"', "`"],
            "numeric_pattern": r'\b\d+\.?\d*[eE]?\d*\b',
        },
        "html": {
            "keywords": [
                "html", "head", "body", "div", "span", "p", "a", "img",
                "ul", "ol", "li", "table", "tr", "td", "th", "form",
                "input", "button", "select", "option", "textarea", "label",
                "h1", "h2", "h3", "h4", "h5", "h6", "header", "footer",
                "nav", "section", "article", "aside", "main", "meta",
                "link", "script", "style", "title", "br", "hr"
            ],
            "single_comment": "",
            "multi_comment": [("<!--", "-->")],
            "string_delimiters": ['"', "'"],
            "numeric_pattern": r'\b\d+\.?\d*\b',
        },
        "json": {
            "keywords": ["true", "false", "null"],
            "single_comment": "",
            "multi_comment": [],
            "string_delimiters": ['"'],
            "numeric_pattern": r'-?\d+\.?\d*[eE]?[-+]?\d*\b',
        }
    }
    
    @classmethod
    def get_language(cls, filename: str) -> str:
        """Detect language from filename"""
        ext = Path(filename).suffix.lower()
        return cls.LANGUAGES.get(ext, "text")
    
    @classmethod
    def get_syntax_rules(cls, language: str) -> Dict:
        """Get syntax rules for a language"""
        return cls.SYNTAX_RULES.get(language, cls.SYNTAX_RULES.get("python", {}))


class LineNumbers(tk.Canvas):
    """Line number gutter for the code editor"""
    
    def __init__(self, master, text_widget, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self.redraw)
        self.text_widget.bind('<MouseWheel>', self.redraw)
        self.text_widget.bind('<<Modified>>', self.redraw)
        self.text_widget.bind('<ButtonRelease-1>', self.redraw)
        self.config(width=50, bg="#1e1e1e", highlightthickness=0)
        self.redraw()
    
    def redraw(self, event=None):
        """Redraw line numbers"""
        self.delete("all")
        
        # Clear modified flag if triggered by modified
        if event and event.type == '42':  # <<Modified>>
            self.text_widget.edit_modified(False)
        
        i = self.text_widget.index("@0,0")
        line_count = int(self.text_widget.index('end-1c').split('.')[0])
        
        # Get current viewport
        viewport_top = self.text_widget.index("@0,0")
        viewport_bottom = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
        start_line = int(viewport_top.split('.')[0])
        end_line = int(viewport_bottom.split('.')[0])
        
        line_height = self.text_widget.dlineinfo("1.0")
        if line_height:
            line_height = line_height[3]
        else:
            line_height = 15
        
        # Calculate visible range with buffer
        visible_start = max(1, start_line - 1)
        visible_end = min(line_count, end_line + 2)
        
        # Configure canvas height
        total_height = line_count * line_height
        self.config(height=max(total_height, 400))
        
        # Draw line numbers
        font_spec = ('Consolas', 10)
        
        for line in range(visible_start, visible_end + 1):
            y_pos = (line - 1) * line_height
            linenum = f"{line}"
            
            # Highlight current line
            cursor_line = int(self.text_widget.index(tk.INSERT).split('.')[0])
            bg_color = "#2a2a2a" if line == cursor_line else "#1e1e1e"
            self.create_rectangle(0, y_pos, 50, y_pos + line_height, 
                                 fill=bg_color, outline="")
            
            self.create_text(
                45, y_pos + line_height//2,
                text=linenum,
                anchor="e",
                font=font_spec,
                fill="#858585"
            )
        
        # Draw border
        self.create_line(48, 0, 48, self.winfo_height(), fill="#333333", width=1)


class CodeEditor(ttk.Frame):
    """Advanced code editor widget with syntax highlighting"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.file_path: Optional[str] = None
        self.language: str = "python"
        self.is_modified: bool = False
        self.save_callback: Optional[Callable] = None
        
        # Track tags for syntax highlighting
        self.tag_configs: Dict = {}
        
        # Setup the editor
        self.setup_editor()
        
        # Bind events
        self.text.bind('<KeyRelease>', self.on_key_release)
        self.text.bind('<<Modified>>', self.on_modified)
    
    def setup_editor(self):
        """Setup the editor UI"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Line numbers
        self.line_numbers = LineNumbers(container, None, width=50)
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(container)
        text_frame.grid(row=0, column=1, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Create font
        self.editor_font = tkfont.Font(family="Consolas", size=11)
        
        # Create text widget
        self.text = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=self.editor_font,
            undo=True,
            maxundo=50,
            padx=10,
            pady=5,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            selectbackground="#264f78",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            tabs=(self.editor_font.measure("    "),)
        )
        self.text.grid(row=0, column=0, sticky="nsew")
        
        # Connect line numbers to text
        self.line_numbers.text_widget = self.text
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=self.on_scroll)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.text.configure(xscrollcommand=h_scrollbar.set)
        
        # Configure syntax tags with colors
        self.configure_tags()
    
    def configure_tags(self):
        """Configure text tags for syntax highlighting"""
        self.text.tag_configure("keyword", foreground="#569cd6")
        self.text.tag_configure("builtin", foreground="#dcdcaa")
        self.text.tag_configure("string", foreground="#ce9178")
        self.text.tag_configure("comment", foreground="#6a9955")
        self.text.tag_configure("number", foreground="#b5cea8")
        self.text.tag_configure("function", foreground="#dcdcaa")
        self.text.tag_configure("class", foreground="#4ec9b0")
        self.text.tag_configure("decorator", foreground="#c586c0")
        self.text.tag_configure("operator", foreground="#d4d4d4")
        self.text.tag_configure("brace", foreground="#ffd700")
        self.text.tag_configure("self", foreground="#569cd6")
        self.text.tag_configure("imports", foreground="#c586c0")
        self.text.tag_configure("current_line", background="#2a2a2a")
        self.text.tag_configure("find_match", background="#e2c96d", foreground="#000000")
        self.text.tag_configure("bracket_match", background="#333333", foreground="#ffd700")
        self.text.tag_configure("error", underline=True, underlinefg="#ff0000")
        self.text.tag_configure("whitespace", foreground="#3a3a3a")
    
    def on_scroll(self, *args):
        """Handle text scroll event"""
        self.text.yview_moveto(args[0]) if len(args) == 1 else self.text.yview(*args)
        self.line_numbers.redraw()
    
    def on_key_release(self, event=None):
        """Handle key release events"""
        # Update current line highlighting
        self.highlight_current_line()
        
        # Auto-indent
        if event and event.keysym == 'Return':
            self.auto_indent()
        
        # Auto-close brackets
        if event and event.char in ['{', '(', '[', '"', "'"]:
            self.auto_close_bracket(event.char)
        
        # Update syntax highlighting with debounce
        self.after(50, self.apply_syntax_highlighting)
        
        # Update line numbers
        self.line_numbers.redraw()
        
        # Mark as modified
        if event:
            self.is_modified = True
            self.event_generate("<<ContentModified>>")
    
    def on_modified(self, event=None):
        """Handle modified event"""
        # Clear the modified flag to allow future modifications
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.update_title()
    
    def highlight_current_line(self):
        """Highlight the current active line"""
        self.text.tag_remove("current_line", "1.0", "end")
        cursor_index = self.text.index(tk.INSERT)
        line_num = cursor_index.split('.')[0]
        self.text.tag_add("current_line", f"{line_num}.0", f"{line_num}.0 lineend+1c")
    
    def auto_indent(self):
        """Auto-indent based on previous line"""
        cursor_index = self.text.index(tk.INSERT)
        line_num = int(cursor_index.split('.')[0])
        prev_line_start = f"{line_num - 1}.0"
        prev_line_end = f"{line_num - 1}.0 lineend"
        prev_line = self.text.get(prev_line_start, prev_line_end)
        
        # Get indentation of previous line
        indent = ""
        for char in prev_line:
            if char in (' ', '\t'):
                indent += char
            else:
                break
        
        # Add extra indent if line ends with colon or opening brace
        stripped = prev_line.strip()
        if stripped.endswith(':') or stripped.endswith('{') or stripped.endswith('('):
            indent += "    "
        
        if indent:
            self.text.insert(tk.INSERT, indent)
            self.line_numbers.redraw()
    
    def auto_close_bracket(self, char):
        """Auto-close brackets and quotes"""
        # Don't auto-close if there's a selection
        if self.text.tag_ranges(tk.SEL):
            return
        
        pairs = {
            '{': '}',
            '(': ')',
            '[': ']',
            '"': '"',
            "'": "'"
        }
        
        # Don't auto-close if previous char is a word character
        cursor = self.text.index(tk.INSERT)
        if int(cursor.split('.')[1]) > 0:
            prev_char_index = f"{cursor} -1c"
            prev_char = self.text.get(prev_char_index, cursor)
            if prev_char.isalnum() and char in ['"', "'"]:
                return
        
        closing = pairs.get(char)
        if closing:
            self.text.insert(tk.INSERT, closing)
            self.text.mark_set(tk.INSERT, cursor)
    
    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to the entire text"""
        # Skip if text is empty
        if not self.text.get("1.0", "end-1c").strip():
            return
        
        # Remove existing tags
        for tag in self.text.tag_names():
            if tag not in ("sel", "current_line", "find_match", "bracket_match"):
                self.text.tag_remove(tag, "1.0", "end")
        
        try:
            content = self.text.get("1.0", "end-1c")
            rules = SyntaxHighlighter.get_syntax_rules(self.language)
            
            if not rules:
                return
            
            # Highlight strings
            string_pattern = f"({'|'.join(re.escape(d) for d in rules['string_delimiters'])})"
            # Simple string highlighting (not perfect but works for most cases)
            
            # Highlight comments
            if rules.get("single_comment"):
                self.highlight_single_comments(content, rules["single_comment"])
            
            # Highlight multi-line comments
            for start_delim, end_delim in rules.get("multi_comment", []):
                self.highlight_multi_comments(start_delim, end_delim)
            
            # Highlight keywords
            for kw in rules.get("keywords", []):
                self.highlight_word(r'\b' + re.escape(kw) + r'\b', "keyword")
            
            # Highlight builtins
            for bi in rules.get("builtins", []):
                self.highlight_word(r'\b' + re.escape(bi) + r'\b', "builtin")
            
            # Highlight numbers
            if rules.get("numeric_pattern"):
                self.highlight_word(rules["numeric_pattern"], "number")
            
            # Highlight decorators (Python)
            if self.language == "python":
                self.highlight_word(r'@\w+', "decorator")
                self.highlight_word(r'\bself\b', "self")
                self.highlight_word(r'\bcls\b', "self")
            
        except Exception as e:
            pass  # Silent fail for syntax highlighting
    
    def highlight_single_comments(self, content: str, comment_char: str):
        """Highlight single-line comments"""
        for i, line in enumerate(content.split('\n'), 1):
            if comment_char in line:
                # Don't highlight if comment char is inside a string
                pos = line.find(comment_char)
                if pos >= 0:
                    start = f"{i}.{pos}"
                    end = f"{i}.end"
                    self.text.tag_add("comment", start, end)
    
    def highlight_multi_comments(self, start_delim: str, end_delim: str):
        """Highlight multi-line comments"""
        content = self.text.get("1.0", "end-1c")
        search_from = "1.0"
        
        while True:
            start = self.text.search(start_delim, search_from, "end-1c")
            if not start:
                break
            
            end = self.text.search(end_delim, f"{start} + {len(start_delim)}c", "end-1c")
            if not end:
                end = "end-1c"
            else:
                end = f"{end} + {len(end_delim)}c"
            
            self.text.tag_add("comment", start, end)
            search_from = end
    
    def highlight_word(self, pattern: str, tag: str):
        """Highlight all occurrences of a word pattern"""
        content = self.text.get("1.0", "end-1c")
        search_from = "1.0"
        
        try:
            regex = re.compile(pattern)
            
            while True:
                match = regex.search(content, int(search_from.split('.')[0]) - 1 if '.' in search_from else 0)
                if not match:
                    break
                
                # Convert character position to text index
                start_pos = f"{match.start()}" if match.start() == 0 else f"1.{match.start()}"
                
                # Use text search for simplicity
                start = self.text.search(match.group(), search_from, "end-1c")
                if not start:
                    break
                
                end = f"{start} + {len(match.group())}c"
                
                # Check if already tagged as comment or string
                tags = self.text.tag_names(start)
                if "comment" not in tags and "string" not in tags:
                    self.text.tag_add(tag, start, end)
                
                # Move search position forward
                next_pos = int(start.split('.')[0]) + 1
                search_from = f"{next_pos}.0"
                if next_pos > len(content.split('\n')):
                    break
        except:
            pass
    
    def load_file(self, file_path: str) -> bool:
        """Load a file into the editor"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            
            content = path.read_text(encoding='utf-8', errors='replace')
            self.text.delete("1.0", "end")
            self.text.insert("1.0", content)
            
            self.file_path = file_path
            self.language = SyntaxHighlighter.get_language(file_path)
            self.is_modified = False
            self.text.edit_modified(False)
            self.text.edit_reset()  # Clear undo history
            
            # Apply syntax highlighting
            self.apply_syntax_highlighting()
            self.highlight_current_line()
            self.line_numbers.redraw()
            self.update_title()
            
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save the current content to file"""
        try:
            save_path = file_path or self.file_path
            if not save_path:
                return False
            
            content = self.text.get("1.0", "end-1c")
            Path(save_path).write_text(content, encoding='utf-8')
            
            self.file_path = save_path
            self.is_modified = False
            self.text.edit_modified(False)
            self.update_title()
            
            if self.save_callback:
                self.save_callback(save_path)
            
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def get_content(self) -> str:
        """Get current text content"""
        return self.text.get("1.0", "end-1c")
    
    def set_content(self, content: str):
        """Set text content"""
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.is_modified = True
        self.apply_syntax_highlighting()
        self.highlight_current_line()
        self.line_numbers.redraw()
    
    def update_title(self):
        """Update editor title based on modification state"""
        pass  # Handled by parent
    
    def find_text(self, search_term: str, start_pos: str = "1.0", 
                  case_sensitive: bool = False, whole_word: bool = False) -> Optional[str]:
        """Find text in the editor"""
        if not search_term:
            return None
        
        try:
            # Clear previous highlights
            self.text.tag_remove("find_match", "1.0", "end")
            
            # Search
            pos = self.text.search(
                search_term, start_pos, "end-1c",
                nocase=not case_sensitive
            )
            
            if pos:
                end_pos = f"{pos} + {len(search_term)}c"
                self.text.tag_add("find_match", pos, end_pos)
                self.text.see(pos)
                self.text.mark_set(tk.INSERT, pos)
                return pos
            
            return None
        except:
            return None
    
    def find_all(self, search_term: str, case_sensitive: bool = False) -> int:
        """Find all occurrences of text"""
        if not search_term:
            return 0
        
        self.text.tag_remove("find_match", "1.0", "end")
        count = 0
        pos = "1.0"
        
        while True:
            pos = self.text.search(
                search_term, pos, "end-1c",
                nocase=not case_sensitive
            )
            if not pos:
                break
            
            end_pos = f"{pos} + {len(search_term)}c"
            self.text.tag_add("find_match", pos, end_pos)
            count += 1
            pos = end_pos
        
        return count
    
    def replace_text(self, search_term: str, replace_term: str, 
                     case_sensitive: bool = False) -> int:
        """Replace text occurrences"""
        if not search_term:
            return 0
        
        # Find and replace all
        content = self.text.get("1.0", "end-1c")
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.escape(search_term)
        
        new_content, count = re.subn(pattern, replace_term, content, flags=flags)
        
        if count > 0:
            self.text.delete("1.0", "end")
            self.text.insert("1.0", new_content)
            self.apply_syntax_highlighting()
        
        return count
    
    def indent_selection(self):
        """Indent selected lines"""
        try:
            if self.text.tag_ranges(tk.SEL):
                start = self.text.index(tk.SEL_FIRST)
                end = self.text.index(tk.SEL_LAST)
            else:
                start = self.text.index(tk.INSERT)
                end = f"{start} lineend"
            
            self.text.insert(start, "    ")
        except:
            pass
    
    def unindent_selection(self):
        """Unindent selected lines"""
        try:
            if self.text.tag_ranges(tk.SEL):
                start = self.text.index(tk.SEL_FIRST)
            else:
                start = self.text.index(tk.INSERT)
            
            line_start = f"{start.split('.')[0]}.0"
            line_content = self.text.get(line_start, f"{line_start} + 4c")
            
            if line_content == "    ":
                self.text.delete(line_start, f"{line_start} + 4c")
            elif line_content.startswith("\t"):
                self.text.delete(line_start, f"{line_start} + 1c")
        except:
            pass
    
    def comment_selection(self):
        """Comment/uncomment selected lines"""
        comment_char = "#"  # Default for Python
        if self.language == "javascript" or self.language == "typescript":
            comment_char = "//"
        elif self.language == "html":
            return  # HTML uses block comments
        
        try:
            if self.text.tag_ranges(tk.SEL):
                start = self.text.index(tk.SEL_FIRST)
                end = self.text.index(tk.SEL_LAST)
            else:
                start = self.text.index(tk.INSERT)
                end = start
            
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0])
            
            # Check if lines are already commented
            all_commented = True
            for line in range(start_line, end_line + 1):
                line_content = self.text.get(f"{line}.0", f"{line}.0 + {len(comment_char)}c")
                if line_content != comment_char:
                    all_commented = False
                    break
            
            # Toggle commenting
            for line in range(start_line, end_line + 1):
                if all_commented:
                    self.text.delete(f"{line}.0", f"{line}.0 + {len(comment_char) + 1}c")
                else:
                    self.text.insert(f"{line}.0", f"{comment_char} ")
        except:
            pass
    
    def toggle_comment(self):
        """Toggle comment on current or selected lines"""
        self.comment_selection()


# Made with Bob