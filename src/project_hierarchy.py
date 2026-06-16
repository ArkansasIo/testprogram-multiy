"""
Project Hierarchy Manager
Manages categories, subcategories, files, folders, modules, submodules with IDs and numbering
"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class NodeType(Enum):
    """Types of nodes in the project hierarchy"""
    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    MODULE = "module"
    SUBMODULE = "submodule"
    FOLDER = "folder"
    SUBFOLDER = "subfolder"
    FILE = "file"
    PART = "part"
    SUBPART = "subpart"
    COMPONENT = "component"


@dataclass
class HierarchyNode:
    """A node in the project hierarchy tree"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    number: int = 0
    name: str = ""
    node_type: NodeType = NodeType.FILE
    parent_id: Optional[str] = None
    children: List['HierarchyNode'] = field(default_factory=list)
    path: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    order: int = 0
    is_active: bool = True
    
    def add_child(self, child: 'HierarchyNode'):
        """Add a child node"""
        child.parent_id = self.id
        child.number = len(self.children) + 1
        child.order = len(self.children)
        self.children.append(child)
    
    def get_child_by_name(self, name: str) -> Optional['HierarchyNode']:
        """Get child by name"""
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_child_by_id(self, node_id: str) -> Optional['HierarchyNode']:
        """Get child by ID"""
        for child in self.children:
            if child.id == node_id:
                return child
        return None
    
    def get_child_by_number(self, number: int) -> Optional['HierarchyNode']:
        """Get child by number"""
        for child in self.children:
            if child.number == number:
                return child
        return None
    
    def get_path_numbers(self) -> str:
        """Get path as numbers (e.g., 1.2.3)"""
        parts = [str(self.number)]
        parent = self.get_parent()
        while parent:
            parts.insert(0, str(parent.number))
            parent = parent.get_parent()
        return ".".join(parts)
    
    def get_path_names(self) -> str:
        """Get path as names (e.g., Category/Subcategory/File)"""
        parts = [self.name]
        parent = self.get_parent()
        while parent:
            parts.insert(0, parent.name)
            parent = parent.get_parent()
        return "/".join(parts)
    
    def get_parent(self, root: Optional['HierarchyNode'] = None):
        """Get parent node (requires root for traversal)"""
        if root is None:
            return None
        
        def find_parent(node: HierarchyNode, target_id: str) -> Optional[HierarchyNode]:
            for child in node.children:
                if child.id == target_id:
                    return node
                result = find_parent(child, target_id)
                if result:
                    return result
            return None
        
        return find_parent(root, self.id)
    
    def find_node_by_id(self, node_id: str) -> Optional['HierarchyNode']:
        """Find a node by ID recursively"""
        if self.id == node_id:
            return self
        for child in self.children:
            result = child.find_node_by_id(node_id)
            if result:
                return result
        return None
    
    def find_nodes_by_type(self, node_type: NodeType) -> List['HierarchyNode']:
        """Find all nodes of a specific type recursively"""
        nodes = []
        if self.node_type == node_type:
            nodes.append(self)
        for child in self.children:
            nodes.extend(child.find_nodes_by_type(node_type))
        return nodes
    
    def find_nodes_by_name(self, name: str, partial: bool = False) -> List['HierarchyNode']:
        """Find nodes by name recursively"""
        nodes = []
        if (partial and name.lower() in self.name.lower()) or (self.name == name):
            nodes.append(self)
        for child in self.children:
            nodes.extend(child.find_nodes_by_name(name, partial))
        return nodes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "number": self.number,
            "name": self.name,
            "node_type": self.node_type.value,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children],
            "path": self.path,
            "description": self.description,
            "metadata": self.metadata,
            "order": self.order,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HierarchyNode':
        """Create from dictionary"""
        node = cls(
            id=data.get("id", str(uuid.uuid4())),
            number=data.get("number", 0),
            name=data.get("name", ""),
            node_type=NodeType(data.get("node_type", "file")),
            parent_id=data.get("parent_id"),
            path=data.get("path", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            order=data.get("order", 0),
            is_active=data.get("is_active", True)
        )
        for child_data in data.get("children", []):
            node.children.append(cls.from_dict(child_data))
        return node


class ProjectHierarchy:
    """Manages the complete project hierarchy with categories and IDs"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.root = HierarchyNode(
            name=project_name,
            node_type=NodeType.CATEGORY,
            number=1,
            description=f"Root category for {project_name}"
        )
        self._id_counter: Dict[str, int] = {}
        self._node_registry: Dict[str, HierarchyNode] = {project_name: self.root}
    
    def add_category(self, name: str, description: str = "") -> HierarchyNode:
        """Add a top-level category"""
        category = HierarchyNode(
            name=name,
            node_type=NodeType.CATEGORY,
            description=description or f"Category: {name}"
        )
        self.root.add_child(category)
        self._node_registry[category.id] = category
        return category
    
    def add_subcategory(self, parent: HierarchyNode, name: str, 
                        description: str = "") -> HierarchyNode:
        """Add a subcategory under a parent"""
        subcategory = HierarchyNode(
            name=name,
            node_type=NodeType.SUBCATEGORY,
            description=description or f"Subcategory: {name}"
        )
        parent.add_child(subcategory)
        self._node_registry[subcategory.id] = subcategory
        return subcategory
    
    def add_module(self, parent: HierarchyNode, name: str, 
                   description: str = "") -> HierarchyNode:
        """Add a module under a parent"""
        module = HierarchyNode(
            name=name,
            node_type=NodeType.MODULE,
            description=description or f"Module: {name}"
        )
        parent.add_child(module)
        self._node_registry[module.id] = module
        return module
    
    def add_submodule(self, parent: HierarchyNode, name: str,
                      description: str = "") -> HierarchyNode:
        """Add a submodule under a parent"""
        submodule = HierarchyNode(
            name=name,
            node_type=NodeType.SUBMODULE,
            description=description or f"Submodule: {name}"
        )
        parent.add_child(submodule)
        self._node_registry[submodule.id] = submodule
        return submodule
    
    def add_folder(self, parent: HierarchyNode, name: str,
                   description: str = "") -> HierarchyNode:
        """Add a folder under a parent"""
        folder = HierarchyNode(
            name=name,
            node_type=NodeType.FOLDER,
            description=description or f"Folder: {name}"
        )
        parent.add_child(folder)
        self._node_registry[folder.id] = folder
        return folder
    
    def add_subfolder(self, parent: HierarchyNode, name: str,
                      description: str = "") -> HierarchyNode:
        """Add a subfolder under a parent"""
        subfolder = HierarchyNode(
            name=name,
            node_type=NodeType.SUBFOLDER,
            description=description or f"Subfolder: {name}"
        )
        parent.add_child(subfolder)
        self._node_registry[subfolder.id] = subfolder
        return subfolder
    
    def add_file(self, parent: HierarchyNode, name: str,
                 file_path: str = "", description: str = "") -> HierarchyNode:
        """Add a file under a parent"""
        file_node = HierarchyNode(
            name=name,
            node_type=NodeType.FILE,
            path=file_path,
            description=description or f"File: {name}"
        )
        parent.add_child(file_node)
        self._node_registry[file_node.id] = file_node
        return file_node
    
    def add_part(self, parent: HierarchyNode, name: str,
                 description: str = "") -> HierarchyNode:
        """Add a part under a parent"""
        part = HierarchyNode(
            name=name,
            node_type=NodeType.PART,
            description=description or f"Part: {name}"
        )
        parent.add_child(part)
        self._node_registry[part.id] = part
        return part
    
    def add_subpart(self, parent: HierarchyNode, name: str,
                    description: str = "") -> HierarchyNode:
        """Add a subpart under a parent"""
        subpart = HierarchyNode(
            name=name,
            node_type=NodeType.SUBPART,
            description=description or f"Subpart: {name}"
        )
        parent.add_child(subpart)
        self._node_registry[subpart.id] = subpart
        return subpart
    
    def get_node(self, node_id: str) -> Optional[HierarchyNode]:
        """Get a node by its ID"""
        return self._node_registry.get(node_id)
    
    def get_node_by_path(self, path_numbers: str) -> Optional[HierarchyNode]:
        """Get node by number path (e.g., '1.2.3')"""
        parts = path_numbers.split('.')
        current = self.root
        for part in parts[1:]:  # Skip root
            num = int(part)
            found = False
            for child in current.children:
                if child.number == num:
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current
    
    def get_all_categories(self) -> List[HierarchyNode]:
        """Get all category nodes"""
        return self.root.find_nodes_by_type(NodeType.CATEGORY)
    
    def get_all_modules(self) -> List[HierarchyNode]:
        """Get all module nodes"""
        return self.root.find_nodes_by_type(NodeType.MODULE)
    
    def get_all_files(self) -> List[HierarchyNode]:
        """Get all file nodes"""
        return self.root.find_nodes_by_type(NodeType.FILE)
    
    def get_hierarchy_tree(self) -> str:
        """Get a text representation of the hierarchy tree"""
        lines = []
        
        def build_tree(node: HierarchyNode, level: int = 0):
            indent = "  " * level
            prefix = ""
            if node.node_type == NodeType.CATEGORY:
                prefix = "📁 "
            elif node.node_type == NodeType.SUBCATEGORY:
                prefix = "📂 "
            elif node.node_type == NodeType.MODULE:
                prefix = "📦 "
            elif node.node_type == NodeType.SUBMODULE:
                prefix = "📎 "
            elif node.node_type == NodeType.FOLDER:
                prefix = "🗂️ "
            elif node.node_type == NodeType.SUBFOLDER:
                prefix = "📁 "
            elif node.node_type == NodeType.FILE:
                prefix = "📄 "
            elif node.node_type == NodeType.PART:
                prefix = "🔧 "
            elif node.node_type == NodeType.SUBPART:
                prefix = "⚙️ "
            else:
                prefix = "• "
            
            path_num = node.get_path_numbers()
            line = f"{indent}{prefix} [{path_num}] ID:{node.id[:8]}... {node.name}"
            if node.description:
                line += f" - {node.description}"
            if node.path:
                line += f" ({node.path})"
            lines.append(line)
            
            for child in node.children:
                build_tree(child, level + 1)
        
        build_tree(self.root)
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert entire hierarchy to dictionary"""
        return {
            "project_name": self.project_name,
            "root": self.root.to_dict(),
            "node_count": len(self._node_registry)
        }
    
    def save_to_file(self, file_path: str):
        """Save hierarchy to a JSON file"""
        data = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ProjectHierarchy':
        """Load hierarchy from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        hierarchy = cls(data["project_name"])
        hierarchy.root = HierarchyNode.from_dict(data["root"])
        
        # Rebuild node registry
        hierarchy._rebuild_registry()
        
        return hierarchy
    
    def _rebuild_registry(self):
        """Rebuild the node ID registry"""
        self._node_registry = {}
        
        def register(node: HierarchyNode):
            self._node_registry[node.id] = node
            for child in node.children:
                register(child)
        
        register(self.root)
    
    def renumber_all(self):
        """Renumber all nodes in the hierarchy"""
        def renumber(node: HierarchyNode, start: int = 1):
            node.number = start
            for i, child in enumerate(node.children, 1):
                renumber(child, i)
        
        renumber(self.root, 1)
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node by ID"""
        node = self.get_node(node_id)
        if node is None or node == self.root:
            return False
        
        parent = node.get_parent(self.root)
        if parent:
            parent.children = [c for c in parent.children if c.id != node_id]
            del self._node_registry[node_id]
            # Remove all descendants from registry
            for descendant in node.find_nodes_by_name("", partial=True):
                if descendant.id in self._node_registry:
                    del self._node_registry[descendant.id]
            self.renumber_all()
            return True
        return False
    
    def move_node(self, node_id: str, new_parent_id: str) -> bool:
        """Move a node to a new parent"""
        node = self.get_node(node_id)
        new_parent = self.get_node(new_parent_id)
        
        if node is None or new_parent is None or node == self.root:
            return False
        if node_id == new_parent_id:
            return False
        # Prevent circular references
        if new_parent.find_node_by_id(node_id) is not None:
            return False
        
        old_parent = node.get_parent(self.root)
        if old_parent:
            old_parent.children = [c for c in old_parent.children if c.id != node_id]
        
        new_parent.add_child(node)
        self.renumber_all()
        return True
    
    def search_nodes(self, query: str, search_type: Optional[NodeType] = None) -> List[HierarchyNode]:
        """Search for nodes by name or description"""
        results = []
        
        def search(node: HierarchyNode):
            if search_type and node.node_type != search_type:
                pass
            elif query.lower() in node.name.lower() or query.lower() in node.description.lower():
                results.append(node)
            for child in node.children:
                search(child)
        
        search(self.root)
        return results


class HierarchyManager:
    """Manages multiple project hierarchies"""
    
    def __init__(self):
        self.hierarchies: Dict[str, ProjectHierarchy] = {}
        self.active_hierarchy: Optional[str] = None
    
    def create_hierarchy(self, project_name: str) -> ProjectHierarchy:
        """Create a new hierarchy for a project"""
        hierarchy = ProjectHierarchy(project_name)
        self.hierarchies[project_name] = hierarchy
        self.active_hierarchy = project_name
        return hierarchy
    
    def get_hierarchy(self, project_name: str) -> Optional[ProjectHierarchy]:
        """Get hierarchy for a project"""
        return self.hierarchies.get(project_name)
    
    def get_active_hierarchy(self) -> Optional[ProjectHierarchy]:
        """Get the currently active hierarchy"""
        if self.active_hierarchy:
            return self.hierarchies.get(self.active_hierarchy)
        return None
    
    def set_active_hierarchy(self, project_name: str) -> bool:
        """Set the active hierarchy"""
        if project_name in self.hierarchies:
            self.active_hierarchy = project_name
            return True
        return False
    
    def delete_hierarchy(self, project_name: str) -> bool:
        """Delete a hierarchy"""
        if project_name in self.hierarchies:
            del self.hierarchies[project_name]
            if self.active_hierarchy == project_name:
                self.active_hierarchy = list(self.hierarchies.keys())[0] if self.hierarchies else None
            return True
        return False
    
    def save_all(self, base_path: str = "projects"):
        """Save all hierarchies to files"""
        for name, hierarchy in self.hierarchies.items():
            file_path = Path(base_path) / name / "hierarchy.json"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            hierarchy.save_to_file(str(file_path))
    
    def load_all(self, base_path: str = "projects"):
        """Load all hierarchies from files"""
        base = Path(base_path)
        if base.exists():
            for project_dir in base.iterdir():
                if project_dir.is_dir():
                    hierarchy_file = project_dir / "hierarchy.json"
                    if hierarchy_file.exists():
                        try:
                            hierarchy = ProjectHierarchy.load_from_file(str(hierarchy_file))
                            self.hierarchies[hierarchy.project_name] = hierarchy
                        except:
                            pass


# Made with Bob