"""
UML Blueprint & Project Management System
Blueprint diagrams, org charts, grid UI, project management dashboard
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from typing import Dict, List, Optional, Tuple, Any, Callable
from pathlib import Path
import json
import math
from enum import Enum
from dataclasses import dataclass, field


class ShapeType(Enum):
    """Types of UML/blueprint shapes"""
    CLASS = "class"
    INTERFACE = "interface"
    ABSTRACT = "abstract"
    ENUM = "enum"
    USE_CASE = "use_case"
    ACTOR = "actor"
    COMPONENT = "component"
    NODE = "node"
    DATABASE = "database"
    FOLDER = "folder"
    FILE = "file"
    MODULE = "module"
    PACKAGE = "package"
    NOTE = "note"
    DECISION = "decision"
    PROCESS = "process"
    TERMINAL = "terminal"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    DIAMOND = "diamond"


class ArrowType(Enum):
    """Types of UML arrows/relationships"""
    ASSOCIATION = "association"
    INHERITANCE = "inheritance"
    IMPLEMENTATION = "implementation"
    DEPENDENCY = "dependency"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    FLOW = "flow"
    MESSAGE = "message"
    RETURN = "return"


@dataclass
class BlueprintNode:
    """A node/element in the blueprint"""
    id: str = ""
    name: str = "Element"
    shape: ShapeType = ShapeType.RECTANGLE
    x: float = 100
    y: float = 100
    width: float = 150
    height: float = 60
    color: str = "#2d2d2d"
    text_color: str = "#ffffff"
    border_color: str = "#569cd6"
    border_width: int = 2
    fields: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    is_expanded: bool = True


@dataclass
class BlueprintArrow:
    """An arrow/relationship in the blueprint"""
    id: str = ""
    source_id: str = ""
    target_id: str = ""
    arrow_type: ArrowType = ArrowType.ASSOCIATION
    label: str = ""
    color: str = "#569cd6"
    width: int = 2
    style: str = "solid"  # solid, dashed, dotted
    source_label: str = ""
    target_label: str = ""


@dataclass
class OrgChartNode:
    """A node in the organization chart"""
    id: str = ""
    name: str = "Position"
    title: str = "Title"
    department: str = ""
    email: str = ""
    avatar: str = ""
    color: str = "#569cd6"
    x: float = 0
    y: float = 0
    children: List['OrgChartNode'] = field(default_factory=list)
    parent_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class BlueprintCanvas(tk.Canvas):
    """Interactive blueprint drawing canvas"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e1e", highlightthickness=0, **kwargs)
        
        self.nodes: Dict[str, BlueprintNode] = {}
        self.arrows: Dict[str, BlueprintArrow] = {}
        self.selected_node: Optional[str] = None
        self.drag_start: Optional[Tuple[float, float]] = None
        self.offset_x: float = 0
        self.offset_y: float = 0
        self.zoom_level: float = 1.0
        self.grid_size: float = 20
        self.show_grid: bool = True
        
        # Bind events
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<MouseWheel>", self.on_zoom)
        self.bind("<ButtonPress-3>", self.on_right_click)
        self.bind("<Configure>", self.on_resize)
        
        # Keyboard shortcuts
        self.bind_all("<Delete>", self.delete_selected)
        self.bind_all("<Control-d>", self.duplicate_selected)
        
        self.setup_grid()
    
    def setup_grid(self):
        """Draw the background grid"""
        self.delete("grid")
        if not self.show_grid:
            return
        
        width = self.winfo_width() or 1000
        height = self.winfo_height() or 800
        
        # Draw minor grid
        for x in range(0, width, int(self.grid_size * self.zoom_level)):
            self.create_line(x, 0, x, height, fill="#2a2a2a", tags="grid")
        for y in range(0, height, int(self.grid_size * self.zoom_level)):
            self.create_line(0, y, width, y, fill="#2a2a2a", tags="grid")
        
        # Draw major grid
        for x in range(0, width, int(self.grid_size * self.zoom_level * 5)):
            self.create_line(x, 0, x, height, fill="#333333", tags="grid")
        for y in range(0, height, int(self.grid_size * self.zoom_level * 5)):
            self.create_line(0, y, width, y, fill="#333333", tags="grid")
    
    def on_resize(self, event):
        """Handle canvas resize"""
        self.setup_grid()
        self.redraw_all()
    
    def on_click(self, event):
        """Handle mouse click"""
        x = event.x / self.zoom_level
        y = event.y / self.zoom_level
        
        # Check if clicking on a node
        clicked_node = self.find_node_at(x, y)
        
        if clicked_node:
            self.selected_node = clicked_node
            self.drag_start = (x - self.nodes[clicked_node].x, 
                              y - self.nodes[clicked_node].y)
            self.highlight_node(clicked_node)
        else:
            self.selected_node = None
            self.clear_highlight()
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.selected_node and self.drag_start:
            x = event.x / self.zoom_level
            y = event.y / self.zoom_level
            
            node = self.nodes[self.selected_node]
            
            # Snap to grid if holding Shift
            if event.state & 0x0001:  # Shift key
                snap = self.grid_size
                node.x = round((x - self.drag_start[0]) / snap) * snap
                node.y = round((y - self.drag_start[1]) / snap) * snap
            else:
                node.x = x - self.drag_start[0]
                node.y = y - self.drag_start[1]
            
            self.redraw_all()
    
    def on_release(self, event):
        """Handle mouse release"""
        self.drag_start = None
    
    def on_zoom(self, event):
        """Handle mouse wheel zoom"""
        # Zoom in/out
        factor = 1.1 if event.delta > 0 else 0.9
        self.zoom_level *= factor
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        
        self.setup_grid()
        self.redraw_all()
    
    def on_right_click(self, event):
        """Handle right click context menu"""
        x = event.x / self.zoom_level
        y = event.y / self.zoom_level
        
        clicked_node = self.find_node_at(x, y)
        
        menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="#ffffff",
                       activebackground="#094771", activeforeground="#ffffff")
        
        if clicked_node:
            menu.add_command(label="Edit Node", command=lambda: self.edit_node(clicked_node))
            menu.add_command(label="Duplicate", command=lambda: self.duplicate_node(clicked_node))
            menu.add_separator()
            menu.add_command(label="Add Child", command=lambda: self.add_child_node(clicked_node))
            menu.add_command(label="Add Arrow From Here", command=lambda: self.start_arrow(clicked_node))
            menu.add_separator()
            menu.add_command(label="Delete", command=lambda: self.delete_node(clicked_node))
        else:
            menu.add_command(label="Add Class", command=lambda: self.add_node_at(x, y, ShapeType.CLASS))
            menu.add_command(label="Add Interface", command=lambda: self.add_node_at(x, y, ShapeType.INTERFACE))
            menu.add_command(label="Add Component", command=lambda: self.add_node_at(x, y, ShapeType.COMPONENT))
            menu.add_command(label="Add Database", command=lambda: self.add_node_at(x, y, ShapeType.DATABASE))
            menu.add_command(label="Add Note", command=lambda: self.add_node_at(x, y, ShapeType.NOTE))
            menu.add_separator()
            menu.add_command(label="Add Rectangle", command=lambda: self.add_node_at(x, y, ShapeType.RECTANGLE))
            menu.add_command(label="Add Diamond", command=lambda: self.add_node_at(x, y, ShapeType.DIAMOND))
            menu.add_separator()
            menu.add_command(label="Paste", command=self.paste_node)
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def find_node_at(self, x: float, y: float) -> Optional[str]:
        """Find a node at the given coordinates"""
        for node_id, node in reversed(list(self.nodes.items())):
            if node.x <= x <= node.x + node.width and node.y <= y <= node.y + node.height:
                return node_id
        return None
    
    def add_node_at(self, x: float, y: float, shape: ShapeType, 
                    name: str = "NewElement") -> str:
        """Add a node at the given position"""
        import uuid
        node_id = str(uuid.uuid4())[:8]
        
        # Set size based on shape
        if shape == ShapeType.NOTE:
            width, height = 200, 100
        elif shape in [ShapeType.CLASS, ShapeType.INTERFACE, ShapeType.ABSTRACT]:
            width, height = 200, 120
        elif shape == ShapeType.DATABASE:
            width, height = 120, 80
        elif shape == ShapeType.DIAMOND:
            width, height = 100, 100
        else:
            width, height = 150, 60
        
        node = BlueprintNode(
            id=node_id,
            name=name,
            shape=shape,
            x=x,
            y=y,
            width=width,
            height=height
        )
        
        # Add default fields/methods for class types
        if shape in [ShapeType.CLASS, ShapeType.INTERFACE, ShapeType.ABSTRACT]:
            node.fields = ["+ attribute: type"]
            node.methods = ["+ method(): return_type"]
        
        self.nodes[node_id] = node
        self.redraw_all()
        return node_id
    
    def add_child_node(self, parent_id: str):
        """Add a child node"""
        if parent_id not in self.nodes:
            return
        
        parent = self.nodes[parent_id]
        child_id = self.add_node_at(
            parent.x + parent.width + 50,
            parent.y + 50,
            ShapeType.CLASS,
            f"{parent.name}_Child"
        )
        
        if child_id:
            self.nodes[child_id].parent_id = parent_id
            parent.children.append(child_id)
            
            # Add inheritance arrow
            self.add_arrow(parent_id, child_id, ArrowType.INHERITANCE)
    
    def add_arrow(self, source_id: str, target_id: str, 
                  arrow_type: ArrowType = ArrowType.ASSOCIATION,
                  label: str = "") -> str:
        """Add an arrow between two nodes"""
        import uuid
        arrow_id = str(uuid.uuid4())[:8]
        
        arrow = BlueprintArrow(
            id=arrow_id,
            source_id=source_id,
            target_id=target_id,
            arrow_type=arrow_type,
            label=label
        )
        
        self.arrows[arrow_id] = arrow
        self.redraw_all()
        return arrow_id
    
    def delete_node(self, node_id: str):
        """Delete a node and its arrows"""
        if node_id not in self.nodes:
            return
        
        # Remove arrows connected to this node
        self.arrows = {aid: a for aid, a in self.arrows.items() 
                      if a.source_id != node_id and a.target_id != node_id}
        
        # Remove from parent
        node = self.nodes[node_id]
        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)
        
        # Delete the node
        del self.nodes[node_id]
        
        if self.selected_node == node_id:
            self.selected_node = None
        
        self.redraw_all()
    
    def duplicate_node(self, node_id: str):
        """Duplicate a node"""
        if node_id not in self.nodes:
            return
        
        original = self.nodes[node_id]
        new_id = self.add_node_at(
            original.x + 30,
            original.y + 30,
            original.shape,
            f"{original.name}_copy"
        )
        
        if new_id:
            new_node = self.nodes[new_id]
            new_node.fields = original.fields.copy()
            new_node.methods = original.methods.copy()
            new_node.color = original.color
            new_node.width = original.width
            new_node.height = original.height
    
    def edit_node(self, node_id: str):
        """Edit node properties"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Create edit dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit: {node.name}")
        dialog.geometry("400x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        name_var = tk.StringVar(value=node.name)
        ttk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        
        # Shape type
        ttk.Label(frame, text="Shape:").grid(row=1, column=0, sticky=tk.W, pady=2)
        shape_var = tk.StringVar(value=node.shape.value)
        shapes = [s.value for s in ShapeType]
        ttk.Combobox(frame, textvariable=shape_var, values=shapes, state="readonly", width=20).grid(
            row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Color
        ttk.Label(frame, text="Color:").grid(row=2, column=0, sticky=tk.W, pady=2)
        color_frame = ttk.Frame(frame)
        color_frame.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        color_var = tk.StringVar(value=node.color)
        color_btn = tk.Button(color_frame, bg=node.color, width=3, height=1,
                              command=lambda: self.choose_color(color_var, color_btn))
        color_btn.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(color_frame, textvariable=color_var, width=15).pack(side=tk.LEFT)
        
        # Fields (for class types)
        if node.shape in [ShapeType.CLASS, ShapeType.INTERFACE, ShapeType.ABSTRACT]:
            ttk.Label(frame, text="Fields:").grid(row=3, column=0, sticky=tk.NW, pady=2)
            
            fields_frame = ttk.Frame(frame)
            fields_frame.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=2)
            
            fields_text = tk.Text(fields_frame, height=4, width=30, bg="#1e1e1e", fg="#d4d4d4",
                                  insertbackground="#ffffff", relief=tk.FLAT, borderwidth=0)
            fields_text.pack(fill=tk.BOTH, expand=True)
            fields_text.insert("1.0", "\n".join(node.fields))
            
            # Methods
            ttk.Label(frame, text="Methods:").grid(row=4, column=0, sticky=tk.NW, pady=2)
            
            methods_frame = ttk.Frame(frame)
            methods_frame.grid(row=4, column=1, sticky="ew", padx=(5, 0), pady=2)
            
            methods_text = tk.Text(methods_frame, height=4, width=30, bg="#1e1e1e", fg="#d4d4d4",
                                   insertbackground="#ffffff", relief=tk.FLAT, borderwidth=0)
            methods_text.pack(fill=tk.BOTH, expand=True)
            methods_text.insert("1.0", "\n".join(node.methods))
        
        def save_changes():
            node.name = name_var.get()
            node.shape = ShapeType(shape_var.get())
            node.color = color_var.get()
            
            if node.shape in [ShapeType.CLASS, ShapeType.INTERFACE, ShapeType.ABSTRACT]:
                node.fields = fields_text.get("1.0", "end-1c").split('\n')
                node.methods = methods_text.get("1.0", "end-1c").split('\n')
            
            self.redraw_all()
            dialog.destroy()
        
        ttk.Button(frame, text="Save", command=save_changes).pack(pady=(20, 0))
        ttk.Button(frame, text="Cancel", command=dialog.destroy).pack(pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def choose_color(self, color_var: tk.StringVar, button: tk.Button):
        """Open color chooser"""
        color = colorchooser.askcolor(color=color_var.get())[1]
        if color:
            color_var.set(color)
            button.config(bg=color)
    
    def highlight_node(self, node_id: str):
        """Highlight a selected node"""
        self.clear_highlight()
        self.selected_node = node_id
    
    def clear_highlight(self):
        """Clear node highlighting"""
        self.selected_node = None
    
    def delete_selected(self, event=None):
        """Delete the selected node"""
        if self.selected_node:
            self.delete_node(self.selected_node)
    
    def duplicate_selected(self, event=None):
        """Duplicate the selected node"""
        if self.selected_node:
            self.duplicate_node(self.selected_node)
    
    def start_arrow(self, node_id: str):
        """Start creating an arrow from a node"""
        self.selected_node = node_id
        self.bind("<ButtonRelease-1>", lambda e: self.finish_arrow(e, node_id))
    
    def finish_arrow(self, event, source_id: str):
        """Finish creating an arrow"""
        x = event.x / self.zoom_level
        y = event.y / self.zoom_level
        
        target_id = self.find_node_at(x, y)
        if target_id and target_id != source_id:
            self.add_arrow(source_id, target_id, ArrowType.ASSOCIATION)
        
        self.unbind("<ButtonRelease-1>")
    
    def paste_node(self):
        """Paste a node from clipboard"""
        try:
            data = self.clipboard_get()
            node_data = json.loads(data)
            node = BlueprintNode(**node_data)
            node.x += 50  # Offset from original
            node.y += 50
            self.nodes[node.id] = node
            self.redraw_all()
        except:
            pass
    
    def redraw_all(self):
        """Redraw all nodes and arrows"""
        self.delete("node")
        self.delete("arrow")
        self.delete("label")
        self.delete("selection")
        
        # Draw arrows
        for arrow in self.arrows.values():
            self.draw_arrow(arrow)
        
        # Draw nodes
        for node in self.nodes.values():
            self.draw_node(node)
        
        # Selection highlight
        if self.selected_node and self.selected_node in self.nodes:
            node = self.nodes[self.selected_node]
            x, y = node.x * self.zoom_level, node.y * self.zoom_level
            w, h = node.width * self.zoom_level, node.height * self.zoom_level
            self.create_rectangle(
                x - 5, y - 5, x + w + 5, y + h + 5,
                outline="#ffd700", width=2, tags="selection", dash=(4, 4)
            )
    
    def draw_node(self, node: BlueprintNode):
        """Draw a single node"""
        x = node.x * self.zoom_level
        y = node.y * self.zoom_level
        w = node.width * self.zoom_level
        h = node.height * self.zoom_level
        
        # Draw shape based on type
        if node.shape == ShapeType.CLASS:
            self.draw_class_shape(x, y, w, h, node)
        elif node.shape == ShapeType.INTERFACE:
            self.draw_interface_shape(x, y, w, h, node)
        elif node.shape == ShapeType.DATABASE:
            self.draw_database_shape(x, y, w, h, node)
        elif node.shape == ShapeType.DIAMOND:
            self.draw_diamond_shape(x, y, w, h, node)
        elif node.shape == ShapeType.NOTE:
            self.draw_note_shape(x, y, w, h, node)
        elif node.shape == ShapeType.ACTOR:
            self.draw_actor_shape(x, y, w, h, node)
        else:
            self.draw_rectangle_shape(x, y, w, h, node)
    
    def draw_class_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a UML class shape"""
        # Main rectangle
        self.create_rectangle(x, y, x + w, y + h, 
                             fill=node.color, outline=node.border_color,
                             width=node.border_width, tags="node")
        
        # Name section
        name_h = max(25, h * 0.25)
        self.create_rectangle(x, y, x + w, y + name_h,
                             outline=node.border_color, width=node.border_width, tags="node")
        
        # Name text
        font_size = max(8, min(12, int(12 * self.zoom_level)))
        self.create_text(x + w/2, y + name_h/2, text=node.name,
                        fill=node.text_color, font=('Arial', font_size, 'bold'),
                        tags="node", anchor="center")
        
        # Fields section
        if node.fields and node.fields[0]:
            field_h = h * 0.35
            self.create_rectangle(x, y + name_h, x + w, y + name_h + field_h,
                                 outline=node.border_color, width=node.border_width, tags="node")
            
            font_size = max(7, min(10, int(10 * self.zoom_level)))
            for i, field in enumerate(node.fields[:5]):  # Max 5 fields visible
                fy = y + name_h + 5 + (i * 14 * self.zoom_level)
                self.create_text(x + 5, fy, text=field.strip(),
                                fill="#ce9178", font=('Consolas', font_size),
                                tags="node", anchor="nw")
        
        # Methods section
        if node.methods and node.methods[0]:
            method_y = y + name_h + (h * 0.35)
            font_size = max(7, min(10, int(10 * self.zoom_level)))
            for i, method in enumerate(node.methods[:5]):
                my = method_y + 5 + (i * 14 * self.zoom_level)
                self.create_text(x + 5, my, text=method.strip(),
                                fill="#dcdcaa", font=('Consolas', font_size),
                                tags="node", anchor="nw")
        
        # Stereotype label for interface/abstract
        if node.shape == ShapeType.INTERFACE:
            self.create_text(x + w - 5, y + name_h - 5, text="<<interface>>",
                            fill="#4ec9b0", font=('Arial', 7), tags="node", anchor="se")
        elif node.shape == ShapeType.ABSTRACT:
            self.create_text(x + w - 5, y + name_h - 5, text="<<abstract>>",
                            fill="#c586c0", font=('Arial', 7), tags="node", anchor="se")
    
    def draw_interface_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw interface shape (circle notation)"""
        self.create_oval(x, y + h/2 - 20, x + 20, y + h/2 + 20,
                        fill=node.color, outline=node.border_color,
                        width=node.border_width, tags="node")
        self.create_text(x + 10, y + h/2, text="I", fill=node.text_color,
                        font=('Arial', 10, 'bold'), tags="node")
        self.create_line(x + 20, y + h/2, x + 30, y + h/2,
                        fill=node.border_color, width=2, tags="node")
        self.create_text(x + w/2, y + h/2, text=node.name, fill=node.text_color,
                        font=('Arial', 10, 'bold'), tags="node")
    
    def draw_database_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a database cylinder shape"""
        # Cylinder body
        self.create_oval(x, y, x + w, y + h * 0.2,
                        fill=node.color, outline=node.border_color,
                        width=node.border_width, tags="node")
        self.create_rectangle(x, y + h * 0.1, x + w, y + h * 0.9,
                            fill=node.color, outline=node.border_color,
                            width=node.border_width, tags="node")
        self.create_oval(x, y + h * 0.8, x + w, y + h,
                        fill=node.color, outline=node.border_color,
                        width=node.border_width, tags="node")
        
        self.create_text(x + w/2, y + h/2, text=node.name,
                        fill=node.text_color, font=('Arial', 10, 'bold'), tags="node")
    
    def draw_diamond_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a diamond/decision shape"""
        points = [x + w/2, y, x + w, y + h/2, x + w/2, y + h, x, y + h/2]
        self.create_polygon(points, fill=node.color, outline=node.border_color,
                          width=node.border_width, tags="node")
        self.create_text(x + w/2, y + h/2, text=node.name,
                        fill=node.text_color, font=('Arial', 10, 'bold'), tags="node")
    
    def draw_note_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a note/sticky note shape"""
        # Folded corner
        fold_size = min(20, w * 0.15)
        points = [x, y, x + w - fold_size, y, x + w, y + fold_size, x + w, y + h, x, y + h]
        self.create_polygon(points, fill="#2d2d2d", outline="#ffd700",
                          width=node.border_width, tags="node")
        # Fold line
        self.create_line(x + w - fold_size, y, x + w - fold_size, y + fold_size, x + w, y + fold_size,
                        fill="#ffd700", width=1, tags="node")
        self.create_text(x + 10, y + 10, text=node.name,
                        fill=node.text_color, font=('Arial', 9), tags="node", anchor="nw")
    
    def draw_actor_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a UML actor (stick figure)"""
        center_x = x + w/2
        
        # Head
        head_r = 10 * self.zoom_level
        self.create_oval(center_x - head_r, y + 5, center_x + head_r, y + 5 + head_r * 2,
                        fill=node.color, outline=node.border_color, tags="node")
        
        # Body
        body_top = y + 5 + head_r * 2
        body_bottom = body_top + 30 * self.zoom_level
        self.create_line(center_x, body_top, center_x, body_bottom,
                        fill=node.border_color, width=2, tags="node")
        
        # Arms
        arm_y = body_top + 12 * self.zoom_level
        self.create_line(center_x - 20 * self.zoom_level, arm_y,
                        center_x + 20 * self.zoom_level, arm_y,
                        fill=node.border_color, width=2, tags="node")
        
        # Legs
        self.create_line(center_x, body_bottom,
                        center_x - 15 * self.zoom_level, body_bottom + 20 * self.zoom_level,
                        fill=node.border_color, width=2, tags="node")
        self.create_line(center_x, body_bottom,
                        center_x + 15 * self.zoom_level, body_bottom + 20 * self.zoom_level,
                        fill=node.border_color, width=2, tags="node")
        
        self.create_text(x + w/2, y + h - 10, text=node.name,
                        fill=node.text_color, font=('Arial', 9, 'bold'), tags="node")
    
    def draw_rectangle_shape(self, x, y, w, h, node: BlueprintNode):
        """Draw a simple rectangle shape"""
        self.create_rectangle(x, y, x + w, y + h,
                            fill=node.color, outline=node.border_color,
                            width=node.border_width, tags="node")
        self.create_text(x + w/2, y + h/2, text=node.name,
                        fill=node.text_color, font=('Arial', 10, 'bold'), tags="node")
    
    def draw_arrow(self, arrow: BlueprintArrow):
        """Draw an arrow between two nodes"""
        if arrow.source_id not in self.nodes or arrow.target_id not in self.nodes:
            return
        
        source = self.nodes[arrow.source_id]
        target = self.nodes[arrow.target_id]
        
        # Calculate start and end points
        sx = (source.x + source.width/2) * self.zoom_level
        sy = (source.y + source.height/2) * self.zoom_level
        tx = (target.x + target.width/2) * self.zoom_level
        ty = (target.y + target.height/2) * self.zoom_level
        
        # Draw line
        line_width = arrow.width * self.zoom_level
        
        if arrow.style == "dashed":
            self.create_line(sx, sy, tx, ty, fill=arrow.color, width=line_width,
                           dash=(8, 4), tags="arrow")
        elif arrow.style == "dotted":
            self.create_line(sx, sy, tx, ty, fill=arrow.color, width=line_width,
                           dash=(2, 4), tags="arrow")
        else:
            self.create_line(sx, sy, tx, ty, fill=arrow.color, width=line_width, tags="arrow")
        
        # Draw arrowhead
        angle = math.atan2(ty - sy, tx - sx)
        arrow_size = 10 * self.zoom_level
        
        if arrow.arrow_type == ArrowType.INHERITANCE:
            # Hollow triangle
            points = self._get_arrowhead_points(tx, ty, angle, arrow_size)
            self.create_polygon(points, fill="", outline=arrow.color,
                              width=line_width, tags="arrow")
        elif arrow.arrow_type == ArrowType.COMPOSITION:
            # Filled diamond
            points = self._get_diamond_points(tx, ty, angle, arrow_size)
            self.create_polygon(points, fill=arrow.color, outline=arrow.color,
                              width=1, tags="arrow")
        else:
            # Regular arrowhead
            points = self._get_arrowhead_points(tx, ty, angle, arrow_size)
            self.create_polygon(points, fill=arrow.color, outline=arrow.color,
                              width=1, tags="arrow")
        
        # Label
        if arrow.label:
            mid_x = (sx + tx) / 2
            mid_y = (sy + ty) / 2
            self.create_text(mid_x, mid_y - 15, text=arrow.label,
                            fill="#888888", font=('Arial', 8), tags="label")
    
    def _get_arrowhead_points(self, x, y, angle, size):
        """Calculate arrowhead triangle points"""
        p1_x = x - size * math.cos(angle - math.pi/6)
        p1_y = y - size * math.sin(angle - math.pi/6)
        p2_x = x - size * math.cos(angle + math.pi/6)
        p2_y = y - size * math.sin(angle + math.pi/6)
        return [x, y, p1_x, p1_y, p2_x, p2_y]
    
    def _get_diamond_points(self, x, y, angle, size):
        """Calculate diamond points for composition"""
        p1_x = x - size * math.cos(angle)
        p1_y = y - size * math.sin(angle)
        p2_x = x - size/2 * math.cos(angle - math.pi/2)
        p2_y = y - size/2 * math.sin(angle - math.pi/2)
        p3_x = x + size * math.cos(angle)
        p3_y = y + size * math.sin(angle)
        p4_x = x - size/2 * math.cos(angle + math.pi/2)
        p4_y = y - size/2 * math.sin(angle + math.pi/2)
        return [p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y]
    
    def to_dict(self) -> Dict:
        """Export blueprint to dictionary"""
        return {
            "nodes": {nid: node.__dict__ for nid, node in self.nodes.items()},
            "arrows": {aid: arrow.__dict__ for aid, arrow in self.arrows.items()}
        }
    
    def load_from_dict(self, data: Dict):
        """Load blueprint from dictionary"""
        self.nodes = {}
        self.arrows = {}
        
        for nid, node_data in data.get("nodes", {}).items():
            node_data.pop("id", None)
            self.nodes[nid] = BlueprintNode(id=nid, **node_data)
        
        for aid, arrow_data in data.get("arrows", {}).items():
            arrow_data.pop("id", None)
            self.arrows[aid] = BlueprintArrow(id=aid, **arrow_data)
        
        self.redraw_all()


class OrgChartWidget(ttk.Frame):
    """Organization chart widget"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.root_node: Optional[OrgChartNode] = None
        self.nodes: Dict[str, OrgChartNode] = {}
        self.node_spacing_x = 200
        self.node_spacing_y = 100
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the org chart UI"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Canvas for drawing
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="#ffffff")
        self.context_menu.add_command(label="Add CEO/CEO", command=self.add_root)
        self.context_menu.add_command(label="Add Manager", command=self.add_manager)
        self.context_menu.add_command(label="Add Employee", command=self.add_employee)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Position", command=self.edit_position)
        self.context_menu.add_command(label="Delete Position", command=self.delete_position)
        
        self.canvas.bind("<ButtonPress-3>", self.show_context_menu)
        
        # Add default root
        self.add_root()
    
    def add_root(self, name: str = "CEO", title: str = "Chief Executive Officer"):
        """Add root node"""
        import uuid
        node = OrgChartNode(
            id=str(uuid.uuid4())[:8],
            name=name,
            title=title,
            department="Executive"
        )
        self.root_node = node
        self.nodes[node.id] = node
        self.render_chart()
    
    def add_manager(self, parent_id: Optional[str] = None, 
                    name: str = "Manager", title: str = "Department Manager"):
        """Add a manager node"""
        import uuid
        parent = self.nodes.get(parent_id) if parent_id else self.root_node
        if not parent:
            return
        
        node = OrgChartNode(
            id=str(uuid.uuid4())[:8],
            name=name,
            title=title,
            department=parent.department,
            parent_id=parent.id
        )
        parent.children.append(node)
        self.nodes[node.id] = node
        self.render_chart()
    
    def add_employee(self, parent_id: Optional[str] = None,
                     name: str = "Employee", title: str = "Team Member"):
        """Add an employee node"""
        import uuid
        parent = self.nodes.get(parent_id) if parent_id else self.root_node
        if not parent:
            return
        
        node = OrgChartNode(
            id=str(uuid.uuid4())[:8],
            name=name,
            title=title,
            department=parent.department,
            parent_id=parent.id
        )
        parent.children.append(node)
        self.nodes[node.id] = node
        self.render_chart()
    
    def render_chart(self):
        """Render the organization chart"""
        self.canvas.delete("all")
        
        if not self.root_node:
            return
        
        # Calculate positions using tree layout
        self._calculate_positions(self.root_node, 400, 50)
        
        # Draw connections first (bottom to top)
        for node in self.nodes.values():
            if node.parent_id and node.parent_id in self.nodes:
                parent = self.nodes[node.parent_id]
                self.canvas.create_line(
                    parent.x, parent.y + 30,
                    node.x, node.y - 20,
                    fill="#569cd6", width=2, smooth=True
                )
        
        # Draw nodes
        for node in self.nodes.values():
            self._draw_org_node(node)
        
        # Set scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _calculate_positions(self, node: OrgChartNode, x: float, y: float, level: int = 0):
        """Calculate tree positions recursively"""
        if not node.children:
            node.x = x
            node.y = y
            return
        
        # Calculate width needed for children
        total_children = len(node.children)
        children_width = (total_children - 1) * self.node_spacing_x
        
        # Position children
        start_x = x - children_width / 2
        for i, child in enumerate(node.children):
            child_x = start_x + i * self.node_spacing_x
            child_y = y + self.node_spacing_y
            self._calculate_positions(child, child_x, child_y, level + 1)
        
        node.x = x
        node.y = y
    
    def _draw_org_node(self, node: OrgChartNode):
        """Draw a single org chart node"""
        x, y = node.x, node.y
        
        # Node rectangle
        self.canvas.create_rectangle(
            x - 80, y - 20, x + 80, y + 20,
            fill="#2d2d2d", outline="#569cd6", width=2,
            tags=("org_node", node.id)
        )
        
        # Name and title
        self.canvas.create_text(x, y - 5, text=node.name,
                               fill="#ffffff", font=('Arial', 10, 'bold'),
                               tags=("org_node", node.id))
        self.canvas.create_text(x, y + 7, text=node.title,
                               fill="#888888", font=('Arial', 8),
                               tags=("org_node", node.id))
        
        # Department label
        if node.department:
            self.canvas.create_text(x, y + 23, text=node.department,
                                   fill="#4ec9b0", font=('Arial', 7),
                                   tags=("org_node", node.id))
        
        # Bind click
        self.canvas.tag_bind(node.id, "<Button-1>", 
                            lambda e, nid=node.id: self.select_node(nid))
    
    def select_node(self, node_id: str):
        """Select a node for editing"""
        self.selected_node_id = node_id
    
    def show_context_menu(self, event):
        """Show context menu"""
        self.context_menu.tk_popup(event.x_root, event.y_root)
    
    def edit_position(self):
        """Edit selected position"""
        if not hasattr(self, 'selected_node_id') or not self.selected_node_id:
            messagebox.showinfo("No Selection", "Please select a position to edit")
            return
        
        node = self.nodes.get(self.selected_node_id)
        if not node:
            return
        
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit: {node.name}")
        dialog.geometry("350x200")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        name_var = tk.StringVar(value=node.name)
        ttk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=2)
        
        ttk.Label(frame, text="Title:").grid(row=1, column=0, sticky=tk.W, pady=2)
        title_var = tk.StringVar(value=node.title)
        ttk.Entry(frame, textvariable=title_var, width=30).grid(row=1, column=1, pady=2)
        
        ttk.Label(frame, text="Department:").grid(row=2, column=0, sticky=tk.W, pady=2)
        dept_var = tk.StringVar(value=node.department)
        ttk.Entry(frame, textvariable=dept_var, width=30).grid(row=2, column=1, pady=2)
        
        def save():
            node.name = name_var.get()
            node.title = title_var.get()
            node.department = dept_var.get()
            self.render_chart()
            dialog.destroy()
        
        ttk.Button(frame, text="Save", command=save).pack(pady=(20, 0))
    
    def delete_position(self):
        """Delete selected position"""
        if not hasattr(self, 'selected_node_id') or not self.selected_node_id:
            return
        
        node = self.nodes.get(self.selected_node_id)
        if not node or node == self.root_node:
            messagebox.showwarning("Cannot Delete", "Cannot delete the root node")
            return
        
        if messagebox.askyesno("Delete", f"Delete {node.name}?"):
            # Remove from parent
            if node.parent_id:
                parent = self.nodes[node.parent_id]
                parent.children = [c for c in parent.children if c.id != node.id]
            
            del self.nodes[node.id]
            self.render_chart()


class GridDashboard(ttk.Frame):
    """Grid dashboard for project management overview"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards: List[Dict] = []
        self.grid_columns = 3
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the grid dashboard UI"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Canvas with scrollbar for scrolling cards
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        v_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Container for cards
        self.cards_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        
        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Add default cards
        self.add_default_cards()
    
    def _on_frame_configure(self, event):
        """Reset scroll region when frame resizes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Adjust card width to fill canvas"""
        width = event.width
        self.canvas.itemconfig(self.canvas_window, width=width)
    
    def add_default_cards(self):
        """Add default dashboard cards"""
        self.add_card("Project Overview", "Current project status and metrics", "#569cd6", [
            ("Status", "Active"),
            ("Files", "42"),
            ("Issues", "3"),
            ("Last Build", "2 hours ago")
        ])
        
        self.add_card("Recent Activity", "Latest project changes", "#4ec9b0", [
            ("Modified", "main.py - 5 min ago"),
            ("Created", "test_api.py - 1 hour ago"),
            ("Updated", "requirements.txt - 2 hours ago"),
            ("Built", "v1.2.0 - 3 hours ago")
        ])
        
        self.add_card("Quick Actions", "Common project tasks", "#c586c0", [
            ("Build Project", "Compile current project"),
            ("Run Tests", "Execute test suite"),
            ("Deploy", "Deploy to production"),
            ("Generate Docs", "Create documentation")
        ])
        
        self.add_card("Team Members", "Project contributors", "#dcdcaa", [
            ("Alice", "Lead Developer"),
            ("Bob", "Backend Developer"),
            ("Charlie", "Frontend Developer"),
            ("David", "DevOps Engineer")
        ])
        
        self.add_card("Dependencies", "Project dependencies status", "#ce9178", [
            ("Python 3.11", "✓ Installed"),
            ("Node.js 18", "✓ Installed"),
            ("Docker", "✓ Running"),
            ("PostgreSQL", "✓ Connected")
        ])
        
        self.add_card("Recent Files", "Recently modified files", "#4ec9b0", [
            ("src/main.py", "Modified"),
            ("src/api.py", "Modified"),
            ("tests/test_main.py", "Created"),
            ("config/settings.py", "Updated")
        ])
        
        self.add_card("Build History", "Recent build results", "#569cd6", [
            ("Build #42", "✓ Success - 5 min ago"),
            ("Build #41", "✓ Success - 1 hour ago"),
            ("Build #40", "✗ Failed - 2 hours ago"),
            ("Build #39", "✓ Success - 3 hours ago")
        ])
        
        self.add_card("Performance", "System performance metrics", "#c586c0", [
            ("CPU Usage", "23%"),
            ("Memory", "1.2 GB / 8 GB"),
            ("Disk", "42 GB / 256 GB"),
            ("Network", "15 Mbps")
        ])
        
        self.layout_cards()
    
    def add_card(self, title: str, description: str, color: str, 
                 items: List[Tuple[str, str]], actions: Optional[List[Dict]] = None):
        """Add a card to the dashboard"""
        self.cards.append({
            "title": title,
            "description": description,
            "color": color,
            "items": items,
            "actions": actions or []
        })
        self.layout_cards()
    
    def layout_cards(self):
        """Layout cards in the grid"""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Create cards in grid
        for i, card_data in enumerate(self.cards):
            row = i // self.grid_columns
            col = i % self.grid_columns
            
            card = self._create_card(self.cards_frame, card_data)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configure grid weights
            self.cards_frame.columnconfigure(col, weight=1)
            self.cards_frame.rowconfigure(row, weight=1)
    
    def _create_card(self, parent, card_data: Dict) -> ttk.Frame:
        """Create a single card widget"""
        card = ttk.Frame(parent, relief="raised")
        card.configure(borderwidth=1)
        
        # Header with color bar
        header = tk.Frame(card, bg="#2d2d2d", height=35)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Color indicator
        color_bar = tk.Frame(header, bg=card_data["color"], width=5)
        color_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(header, text=card_data["title"], 
                 font=('Arial', 11, 'bold'),
                 foreground="#ffffff", background="#2d2d2d").pack(
            side=tk.LEFT, padx=(10, 0), pady=5)
        
        # Description
        desc_frame = tk.Frame(card, bg="#252525")
        desc_frame.pack(fill=tk.X)
        ttk.Label(desc_frame, text=card_data["description"],
                 foreground="#888888", background="#252525",
                 font=('Arial', 8)).pack(anchor=tk.W, padx=10, pady=2)
        
        # Items
        items_frame = tk.Frame(card, bg="#1e1e1e")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for label, value in card_data["items"]:
            item_row = ttk.Frame(items_frame)
            item_row.pack(fill=tk.X, pady=2)
            
            ttk.Label(item_row, text=label, foreground="#d4d4d4",
                     background="#1e1e1e", font=('Arial', 9)).pack(side=tk.LEFT)
            ttk.Label(item_row, text=value, foreground="#ce9178",
                     background="#1e1e1e", font=('Arial', 9)).pack(side=tk.RIGHT)
        
        # Actions
        if card_data["actions"]:
            actions_frame = tk.Frame(card, bg="#252525")
            actions_frame.pack(fill=tk.X)
            
            for action in card_data["actions"]:
                ttk.Button(actions_frame, text=action.get("label", "Action"),
                          command=action.get("command", lambda: None),
                          width=12).pack(side=tk.LEFT, padx=5, pady=5)
        
        return card


class ProjectBlueprintManager:
    """Complete project blueprint and management system"""
    
    def __init__(self, root):
        self.root = root
        self.blueprint_canvas: Optional[BlueprintCanvas] = None
        self.org_chart: Optional[OrgChartWidget] = None
        self.dashboard: Optional[GridDashboard] = None
        
    def create_blueprint_window(self, parent):
        """Create a UML blueprint editor window"""
        window = tk.Toplevel(parent)
        window.title("UML Blueprint Editor")
        window.geometry("1000x700")
        window.minsize(800, 500)
        
        # Toolbar
        toolbar = ttk.Frame(window)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="Add Class", 
                  command=lambda: self.blueprint_canvas.add_node_at(100, 100, ShapeType.CLASS)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Interface",
                  command=lambda: self.blueprint_canvas.add_node_at(100, 100, ShapeType.INTERFACE)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Database",
                  command=lambda: self.blueprint_canvas.add_node_at(100, 100, ShapeType.DATABASE)).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Note",
                  command=lambda: self.blueprint_canvas.add_node_at(100, 100, ShapeType.NOTE)).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="Export", command=self.export_blueprint).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import", command=self.import_blueprint).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear All", 
                  command=lambda: self.blueprint_canvas.nodes.clear() or self.blueprint_canvas.arrows.clear() or self.blueprint_canvas.redraw_all()).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(toolbar, text="  Grid:").pack(side=tk.RIGHT)
        grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, variable=grid_var,
                       command=lambda: setattr(self.blueprint_canvas, 'show_grid', grid_var.get()) or self.blueprint_canvas.setup_grid()).pack(side=tk.RIGHT)
        
        # Canvas
        self.blueprint_canvas = BlueprintCanvas(window)
        self.blueprint_canvas.pack(fill=tk.BOTH, expand=True)
        
        return window
    
    def create_org_chart_window(self, parent):
        """Create an organization chart window"""
        window = tk.Toplevel(parent)
        window.title("Organization Chart")
        window.geometry("800x600")
        window.minsize(600, 400)
        
        self.org_chart = OrgChartWidget(window)
        self.org_chart.pack(fill=tk.BOTH, expand=True)
        
        return window
    
    def create_dashboard_window(self, parent):
        """Create a dashboard window"""
        window = tk.Toplevel(parent)
        window.title("Project Dashboard")
        window.geometry("1000x700")
        window.minsize(800, 500)
        
        self.dashboard = GridDashboard(window)
        self.dashboard.pack(fill=tk.BOTH, expand=True)
        
        return window
    
    def export_blueprint(self):
        """Export blueprint to file"""
        if not self.blueprint_canvas:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            data = self.blueprint_canvas.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Export", "Blueprint exported successfully!")
    
    def import_blueprint(self):
        """Import blueprint from file"""
        if not self.blueprint_canvas:
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.blueprint_canvas.load_from_dict(data)
            messagebox.showinfo("Import", "Blueprint imported successfully!")


# Made with Bob