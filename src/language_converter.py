"""
Language Converter Module
Full-featured multi-language code converter with syntax translation between languages
Supports: Python, JavaScript, TypeScript, C, C++, Java, C#, PHP, Ruby, Go, Rust, Kotlin, Swift
"""
import re
import textwrap
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    
    @classmethod
    def from_extension(cls, ext: str) -> 'Language':
        """Get language from file extension"""
        mapping = {
            '.py': cls.PYTHON,
            '.js': cls.JAVASCRIPT,
            '.jsx': cls.JAVASCRIPT,
            '.ts': cls.TYPESCRIPT,
            '.tsx': cls.TYPESCRIPT,
            '.c': cls.C,
            '.h': cls.C,
            '.cpp': cls.CPP,
            '.cxx': cls.CPP,
            '.hpp': cls.CPP,
            '.java': cls.JAVA,
            '.cs': cls.CSHARP,
            '.php': cls.PHP,
            '.rb': cls.RUBY,
            '.go': cls.GO,
            '.rs': cls.RUST,
            '.kt': cls.KOTLIN,
            '.kts': cls.KOTLIN,
            '.swift': cls.SWIFT,
        }
        return mapping.get(ext.lower(), cls.PYTHON)
    
    @classmethod
    def from_name(cls, name: str) -> 'Language':
        """Get language from name string"""
        for lang in cls:
            if lang.value == name.lower():
                return lang
        return cls.PYTHON
    
    @property
    def extensions(self) -> List[str]:
        """Get file extensions for this language"""
        ext_map = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.mjs'],
            'typescript': ['.ts', '.tsx'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.cxx', '.cc', '.hpp', '.hxx'],
            'java': ['.java'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'go': ['.go'],
            'rust': ['.rs'],
            'kotlin': ['.kt', '.kts'],
            'swift': ['.swift'],
        }
        return ext_map.get(self.value, ['.txt'])


class SyntaxRules:
    """Defines syntax rules for each language"""
    
    # Language syntax templates
    TEMPLATES = {
        Language.PYTHON: {
            "variable": "{name} = {value}",
            "typed_variable": "{name}: {type} = {value}",
            "constant": "{name} = {value}",
            "function": "def {name}({params}):\n    {body}",
            "typed_function": "def {name}({params}) -> {return_type}:\n    {body}",
            "class": "class {name}{inheritance}:\n    {body}",
            "if": "if {condition}:\n    {body}",
            "elif": "elif {condition}:\n    {body}",
            "else": "else:\n    {body}",
            "for": "for {var} in {iterable}:\n    {body}",
            "while": "while {condition}:\n    {body}",
            "do_while": "while True:\n    {body}\n    if not ({condition}):\n        break",
            "switch": None,  # Python 3.10+ match/case
            "match": "match {value}:\n{cases}",
            "case": "    case {pattern}:\n        {body}",
            "try": "try:\n    {body}\nexcept {exception} as e:\n    {handler}",
            "try_finally": "try:\n    {body}\nfinally:\n    {finally_body}",
            "array": "[{items}]",
            "dict": "{{{items}}}",
            "null": "None",
            "true": "True",
            "false": "False",
            "import": "import {module}",
            "from_import": "from {module} import {names}",
            "print": "print({args})",
            "comment": "# {text}",
            "block_comment_start": '"""',
            "block_comment_end": '"""',
            "line_end": "",
            "indent": "    ",
            "self": "self",
            "constructor": "def __init__(self, {params}):\n    {body}",
            "return": "return {value}",
            "break": "break",
            "continue": "continue",
            "pass": "pass",
        },
        Language.JAVASCRIPT: {
            "variable": "let {name} = {value};",
            "typed_variable": "let {name} = {value};",
            "constant": "const {name} = {value};",
            "function": "function {name}({params}) {{\n    {body}\n}}",
            "typed_function": "function {name}({params}) {{\n    {body}\n}}",
            "arrow_function": "const {name} = ({params}) => {{\n    {body}\n}}",
            "class": "class {name}{inheritance} {{\n    {body}\n}}",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for (let {var} of {iterable}) {{\n    {body}\n}}",
            "for_classic": "for ({init}; {condition}; {increment}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "default": "  default:\n    {body}",
            "try": "try {{\n    {body}\n}} catch ({error}) {{\n    {handler}\n}}",
            "try_finally": "try {{\n    {body}\n}} finally {{\n    {finally_body}\n}}",
            "array": "[{items}]",
            "dict": "{{{items}}}",
            "null": "null",
            "true": "true",
            "false": "false",
            "import": "import '{module}'",
            "named_import": "import {{ {names} }} from '{module}'",
            "default_import": "import {name} from '{module}'",
            "print": "console.log({args});",
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "self": "this",
            "constructor": "constructor({params}) {{\n    {body}\n}}",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
        },
        Language.TYPESCRIPT: {
            "variable": "let {name}: {type} = {value};",
            "typed_variable": "let {name}: {type} = {value};",
            "constant": "const {name}: {type} = {value};",
            "function": "function {name}({typed_params}): {return_type} {{\n    {body}\n}}",
            "typed_function": "function {name}({typed_params}): {return_type} {{\n    {body}\n}}",
            "arrow_function": "const {name}: ({typed_params}) => {return_type} = ({params}) => {{\n    {body}\n}}",
            "class": "class {name}{inheritance} {{\n    {body}\n}}",
            "interface": "interface {name} {{\n    {body}\n}}",
            "type": "type {name} = {definition};",
            "enum": "enum {name} {{\n    {values}\n}}",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for (let {var} of {iterable}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "try": "try {{\n    {body}\n}} catch ({error}: {error_type}) {{\n    {handler}\n}}",
            "array": "[{items}]",
            "null": "null",
            "import": "import '{module}'",
            "named_import": "import {{ {names} }} from '{module}'",
            "print": "console.log({args});",
            "comment": "// {text}",
            "line_end": ";",
            "indent": "    ",
            "self": "this",
            "constructor": "constructor({typed_params}) {{\n    {body}\n}}",
            "return": "return {value};",
        },
        Language.C: {
            "variable": "{type} {name} = {value};",
            "typed_variable": "{type} {name} = {value};",
            "constant": "const {type} {name} = {value};",
            "function": "{return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "struct": "struct {name} {{\n    {body}\n}};",
            "union": "union {name} {{\n    {body}\n}};",
            "enum": "enum {name} {{\n    {values}\n}};",
            "typedef": "typedef {existing_type} {new_name};",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for ({init}; {condition}; {increment}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "default": "  default:\n    {body}",
            "array": "{{{items}}}",
            "null": "NULL",
            "true": "1",
            "false": "0",
            "include": "#include <{header}>",
            "local_include": '#include "{header}"',
            "define": "#define {name} {value}",
            "print": 'printf("{format}", {args});',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "main": "int main(int argc, char *argv[]) {{\n    {body}\n    return 0;\n}}",
        },
        Language.CPP: {
            "variable": "{type} {name} = {value};",
            "typed_variable": "{type} {name} = {value};",
            "constant": "const {type} {name} = {value};",
            "auto": "auto {name} = {value};",
            "function": "{return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "class": "class {name}{inheritance} {{\npublic:\n    {body}\n}};",
            "struct": "struct {name} {{\n    {body}\n}};",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for ({init}; {condition}; {increment}) {{\n    {body}\n}}",
            "for_range": "for (auto {var} : {iterable}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "try": "try {{\n    {body}\n}} catch ({exception}) {{\n    {handler}\n}}",
            "array": "{{{items}}}",
            "vector": "std::vector<{type}> {name} = {{{items}}};",
            "null": "nullptr",
            "true": "true",
            "false": "false",
            "include": "#include <{header}>",
            "local_include": '#include "{header}"',
            "namespace": "using namespace {name};",
            "print": 'std::cout << {args} << std::endl;',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "auto_ptr": "std::unique_ptr<{type}> {name} = std::make_unique<{type}>({args});",
        },
        Language.JAVA: {
            "variable": "{type} {name} = {value};",
            "typed_variable": "{type} {name} = {value};",
            "constant": "final {type} {name} = {value};",
            "function": "public {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "private_function": "private {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "protected_function": "protected {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "static_function": "public static {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "class": "public class {name}{inheritance} {{\n    {body}\n}}",
            "abstract_class": "public abstract class {name}{inheritance} {{\n    {body}\n}}",
            "interface": "public interface {name}{inheritance} {{\n    {body}\n}}",
            "enum": "public enum {name} {{\n    {values}\n}}",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for ({type} {var} : {iterable}) {{\n    {body}\n}}",
            "for_classic": "for ({init}; {condition}; {increment}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "try": "try {{\n    {body}\n}} catch ({exception}) {{\n    {handler}\n}}",
            "try_finally": "try {{\n    {body}\n}} finally {{\n    {finally_body}\n}}",
            "array": "new {type}[]{{{items}}}",
            "arraylist": "new ArrayList<{type}>()",
            "null": "null",
            "true": "true",
            "false": "false",
            "import": "import {package};",
            "package": "package {package};",
            "print": 'System.out.println({args});',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "javadoc_start": "/**",
            "javadoc_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "self": "this",
            "constructor": "public {name}({typed_params}) {{\n    {body}\n}}",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "main": "public static void main(String[] args) {{\n    {body}\n}}",
        },
        Language.CSHARP: {
            "variable": "{type} {name} = {value};",
            "typed_variable": "{type} {name} = {value};",
            "constant": "const {type} {name} = {value};",
            "readonly": "readonly {type} {name} = {value};",
            "var": "var {name} = {value};",
            "function": "public {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "private_function": "private {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "static_function": "public static {return_type} {name}({typed_params}) {{\n    {body}\n}}",
            "async_function": "public async Task<{return_type}> {name}({typed_params}) {{\n    {body}\n}}",
            "class": "public class {name}{inheritance} {{\n    {body}\n}}",
            "abstract_class": "public abstract class {name}{inheritance} {{\n    {body}\n}}",
            "interface": "public interface {name}{inheritance} {{\n    {body}\n}}",
            "struct": "public struct {name} {{\n    {body}\n}}",
            "enum": "public enum {name} {{\n    {values}\n}}",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "foreach ({type} {var} in {iterable}) {{\n    {body}\n}}",
            "for_classic": "for ({init}; {condition}; {increment}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "try": "try {{\n    {body}\n}} catch ({exception}) {{\n    {handler}\n}}",
            "try_finally": "try {{\n    {body}\n}} finally {{\n    {finally_body}\n}}",
            "using": "using {namespace};",
            "namespace": "namespace {name} {{\n    {body}\n}}",
            "array": "new {type}[] {{{items}}}",
            "list": "new List<{type}>() {{{items}}}",
            "dict": "new Dictionary<{key_type}, {val_type}>() {{{items}}}",
            "null": "null",
            "true": "true",
            "false": "false",
            "print": 'Console.WriteLine({args});',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "self": "this",
            "constructor": "public {name}({typed_params}) {{\n    {body}\n}}",
            "property": "public {type} {name} {{ get; set; }}",
            "auto_property": "public {type} {name} {{ get; private set; }}",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "main": "static void Main(string[] args) {{\n    {body}\n}}",
            "linq": "from {var} in {source}\nwhere {condition}\nselect {var}",
            "lambda": "({params}) => {expression}",
        },
        Language.PHP: {
            "variable": "${name} = {value};",
            "typed_variable": "{type} ${name} = {value};",
            "constant": "define('{name}', {value});",
            "class_constant": "const {name} = {value};",
            "function": "function {name}({typed_params}): {return_type} {{\n    {body}\n}}",
            "class": "class {name}{inheritance} {{\n    {body}\n}}",
            "abstract_class": "abstract class {name}{inheritance} {{\n    {body}\n}}",
            "interface": "interface {name}{inheritance} {{\n    {body}\n}}",
            "trait": "trait {name} {{\n    {body}\n}}",
            "if": "if ({condition}):\n    {body}\nendif;",
            "if_brace": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "elseif ({condition}):\n    {body}\nendif;",
            "else": "else:\n    {body}\nendif;",
            "for": "foreach (${var} as ${iterable}) {{\n    {body}\n}}",
            "for_classic": "for (${init}; ${condition}; ${increment}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition});",
            "switch": "switch ({value}) {{\n{cases}\n}}",
            "case": "  case {pattern}:\n    {body}\n    break;",
            "try": "try {{\n    {body}\n}} catch ({exception}) {{\n    {handler}\n}}",
            "array": "array({items})",
            "short_array": "[{items}]",
            "assoc_array": "array({key} => {value})",
            "null": "null",
            "true": "true",
            "false": "false",
            "include": "include '{file}';",
            "include_once": "include_once '{file}';",
            "require": "require '{file}';",
            "require_once": "require_once '{file}';",
            "namespace": "namespace {name};",
            "use": "use {class};",
            "print": 'echo {args};',
            "var_dump": 'var_dump({args});',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "self": "$this",
            "parent": "parent::",
            "constructor": "public function __construct({typed_params}) {{\n    {body}\n}}",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "php_open": "<?php",
            "php_close": "?>",
            "echo_tag": "<?= {expression} ?>",
        },
        Language.RUBY: {
            "variable": "{name} = {value}",
            "typed_variable": "{name} = {value}",
            "constant": "{name} = {value}",
            "global": "${name} = {value}",
            "instance": "@{name} = {value}",
            "class_var": "@@{name} = {value}",
            "function": "def {name}({params})\n    {body}\nend",
            "class": "class {name}{inheritance}\n    {body}\nend",
            "module": "module {name}\n    {body}\nend",
            "if": "if {condition}\n    {body}\nend",
            "unless": "unless {condition}\n    {body}\nend",
            "if_else": "if {condition}\n    {body}\nelse\n    {else_body}\nend",
            "if_elsif": "if {condition}\n    {body}\nelsif {elsif_condition}\n    {elsif_body}\nelse\n    {else_body}\nend",
            "for": "for {var} in {iterable} do\n    {body}\nend",
            "each": "{iterable}.each do |{var}|\n    {body}\nend",
            "while": "while {condition} do\n    {body}\nend",
            "until": "until {condition} do\n    {body}\nend",
            "case": "case {value}\nwhen {pattern}\n    {body}\nelse\n    {else_body}\nend",
            "begin": "begin\n    {body}\nrescue {exception} => {var}\n    {handler}\nend",
            "begin_finally": "begin\n    {body}\nensure\n    {finally_body}\nend",
            "array": "[{items}]",
            "hash": "{{{items}}}",
            "symbol": ":{name}",
            "nil": "nil",
            "true": "true",
            "false": "false",
            "require": "require '{module}'",
            "require_relative": "require_relative '{module}'",
            "include_module": "include {module}",
            "extend_module": "extend {module}",
            "print": 'puts {args}',
            "comment": "# {text}",
            "block_comment_start": "=begin",
            "block_comment_end": "=end",
            "line_end": "",
            "indent": "    ",
            "self": "self",
            "constructor": "def initialize({params})\n    {body}\nend",
            "return": "return {value}",
            "break": "break",
            "continue": "next",
            "yield": "yield {args}",
            "block": "{}.each {{ |{var}| {body} }}",
            "lambda": "-> ({params}) {{ {body} }}",
            "attr_reader": "attr_reader :{name}",
            "attr_writer": "attr_writer :{name}",
            "attr_accessor": "attr_accessor :{name}",
        },
        Language.GO: {
            "variable": "var {name} {type} = {value}",
            "short_var": "{name} := {value}",
            "typed_variable": "var {name} {type} = {value}",
            "constant": "const {name} {type} = {value}",
            "function": "func {name}({typed_params}) {return_type} {{\n    {body}\n}}",
            "method": "func (receiver {receiver_type}) {name}({typed_params}) {return_type} {{\n    {body}\n}}",
            "struct": "type {name} struct {{\n    {body}\n}}",
            "interface": "type {name} interface {{\n    {body}\n}}",
            "if": "if {condition} {{\n    {body}\n}}",
            "if_init": "if {init}; {condition} {{\n    {body}\n}}",
            "else_if": "else if {condition} {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "for": "for _, {var} := range {iterable} {{\n    {body}\n}}",
            "for_classic": "for {init}; {condition}; {increment} {{\n    {body}\n}}",
            "for_condition": "for {condition} {{\n    {body}\n}}",
            "while": "for {condition} {{\n    {body}\n}}",
            "switch": "switch {value} {{\n{cases}\n}}",
            "case": "case {pattern}:\n    {body}",
            "default": "default:\n    {body}",
            "select": "select {{\n{cases}\n}}",
            "defer": "defer {function_call}",
            "go_routine": "go {function_call}",
            "chan": "make(chan {type}, {buffer})",
            "array": "[{size}]{type}{{{items}}}",
            "slice": "[]{{type}}{{{items}}}",
            "map": "map[{key_type}]{val_type}{{{items}}}",
            "nil": "nil",
            "true": "true",
            "false": "false",
            "import": "import \"{module}\"",
            "import_group": "import (\n    \"{module}\"\n)",
            "package": "package {name}",
            "print": 'fmt.Println({args})',
            "printf": 'fmt.Sprintf("{format}", {args})',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": "",
            "indent": "\t",
            "return": "return {value}",
            "break": "break",
            "continue": "continue",
            "fallthrough": "fallthrough",
            "error_return": "return {value}, err",
            "error_check": "if err != nil {{\n    return {value}, err\n}}",
            "defer_close": "defer {resource}.Close()",
            "main": "func main() {{\n    {body}\n}}",
        },
        Language.RUST: {
            "variable": "let {mut}{name}: {type} = {value};",
            "mutable": "mut ",
            "constant": "const {name}: {type} = {value};",
            "static": "static {name}: {type} = {value};",
            "function": "fn {name}({typed_params}) -> {return_type} {{\n    {body}\n}}",
            "function_unit": "fn {name}({typed_params}) {{\n    {body}\n}}",
            "struct": "struct {name} {{\n    {body}\n}}",
            "tuple_struct": "struct {name}({types});",
            "enum": "enum {name} {{\n    {values}\n}}",
            "impl": "impl {name} {{\n    {body}\n}}",
            "trait": "trait {name} {{\n    {body}\n}}",
            "impl_for": "impl {trait} for {type} {{\n    {body}\n}}",
            "if": "if {condition} {{\n    {body}\n}}",
            "else_if": "else if {condition} {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "if_let": "if let {pattern} = {value} {{\n    {body}\n}}",
            "for": "for {var} in {iterable} {{\n    {body}\n}}",
            "while": "while {condition} {{\n    {body}\n}}",
            "loop": "loop {{\n    {body}\n}}",
            "match": "match {value} {{\n    {arms}\n}}",
            "match_arm": "    {pattern} => {body},",
            "match_default": "    _ => {body},",
            "array": "[{items}]",
            "vector": "vec![{items}]",
            "hashmap": "HashMap::new()",
            "option": "Option::{value}",
            "result": "Result::{value}",
            "some": "Some({value})",
            "none": "None",
            "ok": "Ok({value})",
            "err": "Err({value})",
            "null": "None",
            "true": "true",
            "false": "false",
            "use": "use {path};",
            "use_as": "use {path} as {alias};",
            "mod": "mod {name};",
            "crate": "extern crate {name};",
            "print": 'println!("{format}", {args});',
            "comment": "// {text}",
            "doc_comment": "/// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": ";",
            "indent": "    ",
            "self": "self",
            "constructor": "fn new({typed_params}) -> Self {{\n    {body}\n}}",
            "return": "return {value};",
            "break": "break;",
            "continue": "continue;",
            "unwrap": "{value}.unwrap()",
            "expect": "{value}.expect(\"{message}\")",
            "match_result": "match {value} {{\n    Ok({ok_var}) => {{ {ok_body} }},\n    Err({err_var}) => {{ {err_body} }},\n}}",
            "if_let_some": "if let Some({var}) = {value} {{\n    {body}\n}}",
            "closure": "|{params}| {{ {body} }}",
            "main": "fn main() {{\n    {body}\n}}",
        },
        Language.KOTLIN: {
            "variable": "var {name}: {type} = {value}",
            "val": "val {name}: {type} = {value}",
            "typed_variable": "var {name}: {type} = {value}",
            "constant": "const val {name}: {type} = {value}",
            "lateinit": "lateinit var {name}: {type}",
            "function": "fun {name}({typed_params}): {return_type} {{\n    {body}\n}}",
            "function_unit": "fun {name}({typed_params}) {{\n    {body}\n}}",
            "single_expr": "fun {name}({typed_params}): {return_type} = {expression}",
            "class": "class {name}{inheritance} {{\n    {body}\n}}",
            "data_class": "data class {name}({constructor_params}) {{\n    {body}\n}}",
            "open_class": "open class {name}{inheritance} {{\n    {body}\n}}",
            "abstract_class": "abstract class {name}{inheritance} {{\n    {body}\n}}",
            "interface": "interface {name} {{\n    {body}\n}}",
            "object": "object {name} {{\n    {body}\n}}",
            "companion": "companion object {{\n    {body}\n}}",
            "enum_class": "enum class {name} {{\n    {values}\n}}",
            "sealed_class": "sealed class {name} {{\n    {body}\n}}",
            "if": "if ({condition}) {{\n    {body}\n}}",
            "else_if": "else if ({condition}) {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "when": "when ({value}) {{\n    {branches}\n}}",
            "when_branch": "    {pattern} -> {body}",
            "when_else": "    else -> {body}",
            "for": "for ({var}: {type} in {iterable}) {{\n    {body}\n}}",
            "while": "while ({condition}) {{\n    {body}\n}}",
            "do_while": "do {{\n    {body}\n}} while ({condition})",
            "try": "try {{\n    {body}\n}} catch (e: {exception}) {{\n    {handler}\n}}",
            "try_finally": "try {{\n    {body}\n}} finally {{\n    {finally_body}\n}}",
            "array": "arrayOf({items})",
            "list": "listOf({items})",
            "mutable_list": "mutableListOf({items})",
            "map": "mapOf({items})",
            "null": "null",
            "true": "true",
            "false": "false",
            "import": "import {package}.*",
            "package": "package {package}",
            "print": 'println({args})',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "line_end": "",
            "indent": "    ",
            "self": "this",
            "constructor": "constructor({typed_params}) {{\n    {body}\n}}",
            "init_block": "init {{\n    {body}\n}}",
            "return": "return {value}",
            "break": "break",
            "continue": "continue",
            "null_safe": "{value}?.",
            "elvis": "{value} ?: {default_value}",
            "lambda": "{{{params}} -> {body}}",
            "suspend": "suspend fun {name}({typed_params}): {return_type} {{\n    {body}\n}}",
            "coroutine": "GlobalScope.launch {{\n    {body}\n}}",
            "main": "fun main(args: Array<String>) {{\n    {body}\n}}",
        },
        Language.SWIFT: {
            "variable": "var {name}: {type} = {value}",
            "let_constant": "let {name}: {type} = {value}",
            "typed_variable": "var {name}: {type} = {value}",
            "constant": "let {name}: {type} = {value}",
            "optional_var": "var {name}: {type}? = {value}",
            "lazy_var": "lazy var {name}: {type} = {value}",
            "computed_var": "var {name}: {type} {{\n    get {{ return {get_expr} }}\n    set {{ {set_body} }}\n}}",
            "function": "func {name}({typed_params}) -> {return_type} {{\n    {body}\n}}",
            "function_void": "func {name}({typed_params}) {{\n    {body}\n}}",
            "class": "class {name}{inheritance} {{\n    {body}\n}}",
            "struct": "struct {name}{inheritance} {{\n    {body}\n}}",
            "enum": "enum {name}{inheritance} {{\n    {values}\n}}",
            "protocol": "protocol {name}{inheritance} {{\n    {body}\n}}",
            "extension": "extension {name} {{\n    {body}\n}}",
            "if": "if {condition} {{\n    {body}\n}}",
            "else_if": "else if {condition} {{\n    {body}\n}}",
            "else": "else {{\n    {body}\n}}",
            "guard": "guard {condition} else {{\n    return\n}}",
            "guard_let": "guard let {name} = {value} else {{\n    return\n}}",
            "switch": "switch {value} {{\n{cases}\n}}",
            "case": "case {pattern}:\n    {body}",
            "default": "default:\n    {body}",
            "for": "for {var} in {iterable} {{\n    {body}\n}}",
            "for_range": "for {var} in {start}...{end} {{\n    {body}\n}}",
            "while": "while {condition} {{\n    {body}\n}}",
            "repeat_while": "repeat {{\n    {body}\n}} while {condition}",
            "do_try": "do {{\n    {body}\n}} catch {{ {error} in\n    {handler}\n}}",
            "do_catch": "do {{\n    {body}\n}} catch {pattern} {{\n    {handler}\n}}",
            "defer": "defer {{\n    {body}\n}}",
            "array": "[{items}]",
            "dict": "[{key}: {value}]",
            "set": "Set<{type}>([{items}])",
            "optional": "{type}?",
            "nil": "nil",
            "true": "true",
            "false": "false",
            "import": "import {module}",
            "print": 'print({args})',
            "comment": "// {text}",
            "block_comment_start": "/*",
            "block_comment_end": "*/",
            "doc_comment": "/// {text}",
            "line_end": "",
            "indent": "    ",
            "self": "self",
            "self_prop": "self.{name}",
            "constructor": "init({typed_params}) {{\n    {body}\n}}",
            "convenience_init": "convenience init({typed_params}) {{\n    {body}\n}}",
            "deinit": "deinit {{\n    {body}\n}}",
            "return": "return {value}",
            "break": "break",
            "continue": "continue",
            "if_let": "if let {name} = {value} {{\n    {body}\n}}",
            "guard_let_early": "guard let {name} = {value} else {{ return }}",
            "closure": "{{ ({params}) -> {return_type} in\n    {body}\n}}",
            "trailing_closure": "{function} {{ ({params}) in\n    {body}\n}}",
            "map_closure": "{array}.map {{ {item} in {expression} }}",
            "filter_closure": "{array}.filter {{ {item} in {condition} }}",
            "reduce_closure": "{array}.reduce({initial}) {{ {result}, {item} in {expression} }}",
            "main": "import Foundation\n\nfunc main() {{\n    {body}\n}}\n\nmain()",
        },
    }
    
    # Type mapping between languages
    TYPE_MAP: Dict[Tuple[Language, Language], Dict[str, str]] = {}
    
    # Common type equivalents across languages
    COMMON_TYPES = {
        "int": {"python": "int", "javascript": "Number", "typescript": "number", 
                "c": "int", "cpp": "int", "java": "int", "csharp": "int",
                "php": "int", "ruby": "Integer", "go": "int", "rust": "i32",
                "kotlin": "Int", "swift": "Int"},
        "float": {"python": "float", "javascript": "Number", "typescript": "number",
                  "c": "float", "cpp": "float", "java": "float", "csharp": "float",
                  "php": "float", "ruby": "Float", "go": "float64", "rust": "f64",
                  "kotlin": "Float", "swift": "Float"},
        "double": {"python": "float", "javascript": "Number", "typescript": "number",
                   "c": "double", "cpp": "double", "java": "double", "csharp": "double",
                   "php": "float", "ruby": "Float", "go": "float64", "rust": "f64",
                   "kotlin": "Double", "swift": "Double"},
        "string": {"python": "str", "javascript": "String", "typescript": "string",
                   "c": "char*", "cpp": "std::string", "java": "String", "csharp": "string",
                   "php": "string", "ruby": "String", "go": "string", "rust": "String",
                   "kotlin": "String", "swift": "String"},
        "bool": {"python": "bool", "javascript": "Boolean", "typescript": "boolean",
                 "c": "int", "cpp": "bool", "java": "boolean", "csharp": "bool",
                 "php": "bool", "ruby": "Boolean", "go": "bool", "rust": "bool",
                 "kotlin": "Boolean", "swift": "Bool"},
        "void": {"python": "None", "javascript": "undefined", "typescript": "void",
                 "c": "void", "cpp": "void", "java": "void", "csharp": "void",
                 "php": "void", "ruby": "nil", "go": "", "rust": "()",
                 "kotlin": "Unit", "swift": "Void"},
        "list": {"python": "list", "javascript": "Array", "typescript": "Array",
                 "c": "struct", "cpp": "std::vector", "java": "ArrayList", "csharp": "List",
                 "php": "array", "ruby": "Array", "go": "[]", "rust": "Vec",
                 "kotlin": "List", "swift": "Array"},
        "dict": {"python": "dict", "javascript": "Object", "typescript": "Record",
                 "c": "struct", "cpp": "std::map", "java": "HashMap", "csharp": "Dictionary",
                 "php": "assoc_array", "ruby": "Hash", "go": "map", "rust": "HashMap",
                 "kotlin": "Map", "swift": "Dictionary"},
        "any": {"python": "Any", "javascript": "any", "typescript": "any",
                "c": "void*", "cpp": "void*", "java": "Object", "csharp": "object",
                "php": "mixed", "ruby": "Object", "go": "interface{}", "rust": "Box<dyn Any>",
                "kotlin": "Any", "swift": "Any"},
    }
    
    @classmethod
    def get_template(cls, language: Language, template_name: str) -> Optional[str]:
        """Get a syntax template for a specific language"""
        templates = cls.TEMPLATES.get(language, {})
        return templates.get(template_name)
    
    @classmethod
    def convert_type(cls, type_name: str, from_lang: Language, to_lang: Language) -> str:
        """Convert a type name from one language to another"""
        # Check common types first
        for category, languages in cls.COMMON_TYPES.items():
            if from_lang.value in languages and languages[from_lang.value] == type_name:
                return languages.get(to_lang.value, type_name)
            # Also check if the type matches any category in common types
            if to_lang.value in languages and type_name.lower() == category:
                return languages[to_lang.value]
        
        # Return original if no mapping found
        return type_name


class CodeBlock:
    """Represents a parsed code block for conversion"""
    
    def __init__(self, block_type: str, content: Dict[str, Any]):
        self.block_type = block_type
        self.content = content
        self.children: List['CodeBlock'] = []
        self.indent_level: int = 0
    
    def add_child(self, child: 'CodeBlock'):
        """Add a child block"""
        self.children.append(child)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "type": self.block_type,
            "content": self.content,
            "children": [c.to_dict() for c in self.children],
            "indent": self.indent_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeBlock':
        """Create from dictionary"""
        block = cls(data["type"], data["content"])
        block.indent_level = data.get("indent", 0)
        for child_data in data.get("children", []):
            block.add_child(cls.from_dict(child_data))
        return block


class CodeParser:
    """Parses source code into intermediate representation"""
    
    @staticmethod
    def parse_python(code: str) -> List[CodeBlock]:
        """Parse Python code into blocks"""
        blocks = []
        lines = code.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                i += 1
                continue
            
            # Class definition
            class_match = re.match(r'class\s+(\w+)(?:\(([^)]*)\))?\s*:', stripped)
            if class_match:
                block = CodeBlock("class", {
                    "name": class_match.group(1),
                    "inheritance": class_match.group(2) or ""
                })
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or 
                                          not lines[i].strip()):
                    if lines[i].strip():
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            
            # Function definition
            func_match = re.match(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:', stripped)
            if func_match:
                block = CodeBlock("function", {
                    "name": func_match.group(1),
                    "params": func_match.group(2),
                    "return_type": (func_match.group(3) or "").strip()
                })
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or
                                          not lines[i].strip()):
                    if lines[i].strip():
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            
            # If/elif/else
            if_match = re.match(r'(elif|if)\s+(.+)\s*:', stripped)
            elif_match = re.match(r'else\s*:', stripped)
            if if_match:
                block = CodeBlock("if", {"condition": if_match.group(2)})
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or
                                          not lines[i].strip()):
                    if lines[i].strip() and not re.match(r'else|elif', lines[i].strip()):
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            elif elif_match:
                blocks.append(CodeBlock("else", {}))
                i += 1
                continue
            
            # For loop
            for_match = re.match(r'for\s+(\w+)\s+in\s+(.+)\s*:', stripped)
            if for_match:
                block = CodeBlock("for", {
                    "var": for_match.group(1),
                    "iterable": for_match.group(2).strip()
                })
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or
                                          not lines[i].strip()):
                    if lines[i].strip():
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            
            # While loop
            while_match = re.match(r'while\s+(.+)\s*:', stripped)
            if while_match:
                block = CodeBlock("while", {"condition": while_match.group(1).strip()})
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or
                                          not lines[i].strip()):
                    if lines[i].strip():
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            
            # Try/except
            try_match = re.match(r'try\s*:', stripped)
            if try_match:
                block = CodeBlock("try", {})
                base_indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip()) > base_indent or
                                          not lines[i].strip()):
                    if lines[i].strip() and not lines[i].strip().startswith('except') and \
                       not lines[i].strip().startswith('finally'):
                        block.add_child(CodeBlock("line", {"text": lines[i]}))
                    i += 1
                blocks.append(block)
                continue
            
            # Import
            import_match = re.match(r'import\s+(.+)', stripped)
            if import_match:
                blocks.append(CodeBlock("import", {"module": import_match.group(1)}))
                i += 1
                continue
            
            from_match = re.match(r'from\s+(\S+)\s+import\s+(.+)', stripped)
            if from_match:
                blocks.append(CodeBlock("from_import", {
                    "module": from_match.group(1),
                    "names": from_match.group(2)
                }))
                i += 1
                continue
            
            # Variable assignment
            var_match = re.match(r'(\w+)\s*:\s*(\w+)\s*=\s*(.+)', stripped)
            if var_match:
                blocks.append(CodeBlock("typed_variable", {
                    "name": var_match.group(1),
                    "type": var_match.group(2),
                    "value": var_match.group(3)
                }))
                i += 1
                continue
            
            var_simple = re.match(r'(\w+)\s*=\s*(.+)', stripped)
            if var_simple and not stripped.startswith('def ') and not stripped.startswith('class '):
                blocks.append(CodeBlock("variable", {
                    "name": var_simple.group(1),
                    "value": var_simple.group(2)
                }))
                i += 1
                continue
            
            # Return
            if stripped.startswith('return '):
                blocks.append(CodeBlock("return", {"value": stripped[7:]}))
                i += 1
                continue
            
            # Print
            print_match = re.match(r'print\s*\((.+)\)', stripped)
            if print_match:
                blocks.append(CodeBlock("print", {"args": print_match.group(1)}))
                i += 1
                continue
            
            # Default line
            blocks.append(CodeBlock("line", {"text": line}))
            i += 1
        
        return blocks
    
    @staticmethod
    def parse_javascript(code: str) -> List[CodeBlock]:
        """Parse JavaScript/TypeScript code into blocks"""
        blocks = []
        # Remove block comments
        code = re.sub(r'/\*[\s\S]*?\*/', '', code)
        lines = code.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('//'):
                i += 1
                continue
            
            # Class definition
            class_match = re.match(r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{', stripped)
            if class_match:
                block = CodeBlock("class", {
                    "name": class_match.group(1),
                    "extends": class_match.group(2) or "",
                    "implements": class_match.group(3) or ""
                })
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # Function definition
            func_match = re.match(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*\{', stripped)
            if func_match:
                block = CodeBlock("function", {
                    "name": func_match.group(1),
                    "params": func_match.group(2)
                })
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # Arrow function
            arrow_match = re.match(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>\s*\{', stripped)
            if arrow_match:
                block = CodeBlock("arrow_function", {
                    "name": arrow_match.group(1),
                    "params": arrow_match.group(2)
                })
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # If statement
            if_match = re.match(r'if\s*\(([^)]*)\)\s*\{', stripped)
            if if_match:
                block = CodeBlock("if", {"condition": if_match.group(1)})
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # For loop
            for_match = re.match(r'for\s*\(([^)]+)\)\s*\{', stripped)
            if for_match:
                for_content = for_match.group(1)
                # Check if it's a for-of loop
                for_of = re.match(r'(?:const|let|var)\s+(\w+)\s+of\s+(.+)', for_content)
                if for_of:
                    block = CodeBlock("for", {
                        "var": for_of.group(1),
                        "iterable": for_of.group(2).strip()
                    })
                else:
                    block = CodeBlock("for_classic", {"init": for_content})
                
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # While loop
            while_match = re.match(r'while\s*\(([^)]*)\)\s*\{', stripped)
            if while_match:
                block = CodeBlock("while", {"condition": while_match.group(1)})
                brace_count = 1
                i += 1
                body_lines = []
                while i < len(lines) and brace_count > 0:
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    if brace_count > 0:
                        body_lines.append(lines[i])
                    i += 1
                for bline in body_lines:
                    block.add_child(CodeBlock("line", {"text": bline}))
                blocks.append(block)
                continue
            
            # Variable declarations
            var_match = re.match(r'(?:let|const|var)\s+(\w+)(?:\s*:\s*(\w+))?\s*=\s*(.+);?$', stripped)
            if var_match:
                blocks.append(CodeBlock("variable", {
                    "name": var_match.group(1),
                    "type": var_match.group(2) or "",
                    "value": var_match.group(3)
                }))
                i += 1
                continue
            
            # Return
            return_match = re.match(r'return\s+(.+);?$', stripped)
            if return_match:
                blocks.append(CodeBlock("return", {"value": return_match.group(1)}))
                i += 1
                continue
            
            # Import
            import_match = re.match(r'import\s+\{([^}]+)\}\s+from\s+[\'"]([^\'"]+)[\'"]', stripped)
            if import_match:
                blocks.append(CodeBlock("named_import", {
                    "names": import_match.group(1),
                    "module": import_match.group(2)
                }))
                i += 1
                continue
            
            import_default = re.match(r'import\s+(\w+)\s+from\s+[\'"]([^\'"]+)[\'"]', stripped)
            if import_default:
                blocks.append(CodeBlock("default_import", {
                    "name": import_default.group(1),
                    "module": import_default.group(2)
                }))
                i += 1
                continue
            
            # Console.log
            console_match = re.match(r'console\.log\s*\((.+)\);?$', stripped)
            if console_match:
                blocks.append(CodeBlock("print", {"args": console_match.group(1)}))
                i += 1
                continue
            
            # Default line
            blocks.append(CodeBlock("line", {"text": line}))
            i += 1
        
        return blocks
    
    @staticmethod
    def parse_code(code: str, language: Language) -> List[CodeBlock]:
        """Parse code based on language"""
        if language in [Language.PYTHON]:
            return CodeParser.parse_python(code)
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return CodeParser.parse_javascript(code)
        elif language in [Language.C, Language.CPP, Language.JAVA, Language.CSHARP]:
            return CodeParser.parse_javascript(code)  # Similar syntax
        elif language == Language.PHP:
            # Remove PHP tags first
            code_clean = re.sub(r'<\?php\s*', '', code)
            code_clean = re.sub(r'\?>', '', code_clean)
            return CodeParser.parse_javascript(code_clean)
        elif language == Language.RUBY:
            return CodeParser.parse_python(code)
        elif language == Language.GO:
            return CodeParser.parse_javascript(code)
        elif language == Language.RUST:
            return CodeParser.parse_javascript(code)
        elif language in [Language.KOTLIN, Language.SWIFT]:
            return CodeParser.parse_javascript(code)
        else:
            return [CodeBlock("line", {"text": line}) for line in code.split('\n')]


class CodeWriter:
    """Writes intermediate representation to target language code"""
    
    def __init__(self, target_language: Language):
        self.target = target_language
        self.indent_str = SyntaxRules.get_template(target_language, "indent") or "    "
        self.line_end = SyntaxRules.get_template(target_language, "line_end") or ""
    
    def write_block(self, block: CodeBlock, indent_level: int = 0) -> str:
        """Convert a code block to target language code"""
        indent = self.indent_str * indent_level
        result = ""
        
        if block.block_type == "line":
            text = block.content.get("text", "")
            # Keep the original line's indentation converted to target style
            result = indent + text.strip() + "\n"
        
        elif block.block_type == "variable":
            template = SyntaxRules.get_template(self.target, "variable")
            if template:
                result = indent + template.format(
                    name=block.content.get("name", ""),
                    type=block.content.get("type", "auto"),
                    value=block.content.get("value", "")
                )
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "typed_variable":
            template = SyntaxRules.get_template(self.target, "typed_variable")
            if not template:
                template = SyntaxRules.get_template(self.target, "variable") or "{name} = {value}"
            type_name = SyntaxRules.convert_type(
                block.content.get("type", "auto"),
                Language.PYTHON,  # Default source type
                self.target
            )
            result = indent + template.format(
                name=block.content.get("name", ""),
                type=type_name,
                value=block.content.get("value", "")
            )
            if not result.endswith("\n"):
                result += "\n"
        
        elif block.block_type == "function":
            template = SyntaxRules.get_template(self.target, "function")
            if template:
                params = self._convert_params(block.content.get("params", ""))
                return_type = SyntaxRules.convert_type(
                    block.content.get("return_type", "void"),
                    Language.PYTHON,
                    self.target
                )
                
                # Build body from children
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                result = indent + template.format(
                    name=block.content.get("name", ""),
                    params=params,
                    typed_params=params,
                    return_type=return_type or "void",
                    body=body
                )
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "class":
            template = SyntaxRules.get_template(self.target, "class")
            if template:
                inheritance = block.content.get("inheritance", "")
                if inheritance:
                    if self.target in [Language.JAVA, Language.CSHARP]:
                        inheritance = f" extends {inheritance}"
                    elif self.target in [Language.CPP, Language.KOTLIN]:
                        inheritance = f" : {inheritance}"
                    elif self.target == Language.PYTHON:
                        inheritance = f"({inheritance})"
                    elif self.target == Language.SWIFT:
                        inheritance = f": {inheritance}"
                    else:
                        inheritance = f" extends {inheritance}"
                
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                result = indent + template.format(
                    name=block.content.get("name", ""),
                    inheritance=inheritance,
                    body=body
                )
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "if":
            template = SyntaxRules.get_template(self.target, "if")
            if template:
                condition = block.content.get("condition", "")
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                result = indent + template.format(
                    condition=condition,
                    body=body
                )
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "else":
            template = SyntaxRules.get_template(self.target, "else")
            if template:
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                result = indent + template.format(body=body)
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "for":
            template = SyntaxRules.get_template(self.target, "for")
            if template:
                var = block.content.get("var", "i")
                iterable = block.content.get("iterable", "[]")
                
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                # Adapt to target language syntax
                if self.target == Language.PYTHON:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                elif self.target in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                elif self.target in [Language.GO]:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                elif self.target in [Language.RUST, Language.KOTLIN]:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                elif self.target in [Language.JAVA, Language.CSHARP]:
                    result = indent + template.format(type="var", var=var, iterable=iterable, body=body)
                elif self.target == Language.SWIFT:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                else:
                    result = indent + template.format(var=var, iterable=iterable, body=body)
                
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "while":
            template = SyntaxRules.get_template(self.target, "while")
            if template:
                condition = block.content.get("condition", "")
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                result = indent + template.format(condition=condition, body=body)
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "return":
            template = SyntaxRules.get_template(self.target, "return")
            if template:
                value = block.content.get("value", "")
                result = indent + template.format(value=value)
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "print":
            template = SyntaxRules.get_template(self.target, "print")
            if template:
                args = block.content.get("args", "")
                result = indent + template.format(args=args)
                if not result.endswith("\n"):
                    result += "\n"
        
        elif block.block_type == "import":
            if self.target in [Language.C, Language.CPP]:
                template = "$include <{module}>"
                result = indent + template.replace("$include", "#include").format(module=block.content.get("module", "")) + "\n"
            elif self.target in [Language.JAVA, Language.KOTLIN]:
                template = SyntaxRules.get_template(self.target, "import")
                if template:
                    result = indent + template.format(package=block.content.get("module", "")) + "\n"
            elif self.target == Language.GO:
                result = indent + f'import "{block.content.get("module", "")}"\n'
            elif self.target == Language.RUST:
                result = indent + f'use {block.content.get("module", "")};\n'
            elif self.target == Language.PHP:
                result = indent + f'require_once \'{block.content.get("module", "")}\';\n'
            elif self.target == Language.RUBY:
                result = indent + f'require \'{block.content.get("module", "")}\'\n'
            else:
                result = indent + f'import \'{block.content.get("module", "")}\'\n'
        
        elif block.block_type == "from_import":
            module = block.content.get("module", "")
            names = block.content.get("names", "")
            if self.target in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
                result = indent + f'import {{ {names} }} from \'{module}\'\n'
            elif self.target == Language.PYTHON:
                result = indent + f'from {module} import {names}\n'
            elif self.target in [Language.JAVA]:
                result = indent + f'import {module}.{names};\n'
            elif self.target in [Language.CSHARP]:
                result = indent + f'using {module};\n'
            elif self.target == Language.GO:
                result = indent + f'import "{module}"\n'
            elif self.target == Language.RUST:
                names_clean = names.replace(",", ", ").strip()
                result = indent + f'use {module}::{{{names_clean}}};\n'
            else:
                result = indent + f'// from {module} import {names}\n'
        
        elif block.block_type == "named_import":
            result = indent + f'import {{ {block.content.get("names", "")} }} from \'{block.content.get("module", "")}\'\n'
        
        elif block.block_type == "default_import":
            result = indent + f'import {block.content.get("name", "")} from \'{block.content.get("module", "")}\'\n'
        
        elif block.block_type == "try":
            template = SyntaxRules.get_template(self.target, "try")
            if template:
                body = ""
                for child in block.children:
                    body += self.write_block(child, indent_level + 1)
                
                exception_type = "Exception"
                if self.target == Language.PYTHON:
                    exception_type = "Exception"
                elif self.target in [Language.CPP, Language.JAVA, Language.CSHARP, Language.KOTLIN]:
                    exception_type = "Exception"
                elif self.target == Language.RUST:
                    exception_type = "e"
                elif self.target == Language.SWIFT:
                    exception_type = "error"
                
                result = indent + template.format(
                    body=body,
                    exception=exception_type,
                    error="e",
                    handler="// TODO: handle error"
                )
                if not result.endswith("\n"):
                    result += "\n"
        
        else:
            # Unknown block types, just output the content as-is
            if hasattr(block, 'content'):
                for key, value in block.content.items():
                    if isinstance(value, str):
                        result += indent + value + "\n"
                        break
        
        return result
    
    def _convert_params(self, params: str) -> str:
        """Convert function parameters to target language format"""
        if not params or params.strip() == "":
            return ""
        
        param_list = [p.strip() for p in params.split(',')]
        converted = []
        
        for param in param_list:
            if not param:
                continue
            
            # Handle typed parameters (Python: name: type)
            typed_match = re.match(r'(\w+)\s*:\s*(\w+)', param)
            if typed_match:
                name = typed_match.group(1)
                type_name = SyntaxRules.convert_type(
                    typed_match.group(2), Language.PYTHON, self.target
                )
                
                if self.target in [Language.PYTHON, Language.KOTLIN]:
                    converted.append(f"{name}: {type_name}")
                elif self.target in [Language.TYPESCRIPT]:
                    converted.append(f"{name}: {type_name}")
                elif self.target in [Language.C, Language.CPP, Language.JAVA, Language.CSHARP, Language.GO]:
                    converted.append(f"{type_name} {name}")
                elif self.target == Language.RUST:
                    converted.append(f"{name}: {type_name}")
                elif self.target == Language.SWIFT:
                    converted.append(f"{name}: {type_name}")
                elif self.target in [Language.JAVASCRIPT, Language.PHP, Language.RUBY]:
                    converted.append(name)
                else:
                    converted.append(f"{name}: {type_name}")
            else:
                # Simple parameter (no type)
                if self.target in [Language.C, Language.CPP, Language.JAVA]:
                    converted.append(f"auto {param}")
                elif self.target == Language.CSHARP:
                    converted.append(f"var {param}")
                elif self.target == Language.GO:
                    converted.append(f"{param} interface{{}}")
                elif self.target == Language.TYPESCRIPT:
                    converted.append(f"{param}: any")
                else:
                    converted.append(param)
        
        return ", ".join(converted)
    
    def write_blocks(self, blocks: List[CodeBlock]) -> str:
        """Convert a list of blocks to code"""
        result = ""
        
        # Add language-specific headers
        if self.target == Language.PHP:
            result += "<?php\n\n"
        elif self.target == Language.GO:
            result += "package main\n\n"
        elif self.target == Language.JAVA:
            result += "public class Main {\n"
        elif self.target == Language.C:
            result += "#include <stdio.h>\n#include <stdlib.h>\n\n"
        elif self.target == Language.CPP:
            result += "#include <iostream>\n#include <vector>\n#include <string>\n\n"
        elif self.target == Language.RUST:
            result += "fn main() {\n    println!(\"Hello, world!\");\n}\n\n"
        
        for block in blocks:
            result += self.write_block(block, 0)
        
        # Close language-specific blocks
        if self.target == Language.JAVA:
            result += "}\n"
        
        return result


class LanguageConverter:
    """Main language converter class"""
    
    def __init__(self):
        self.supported_languages = [lang for lang in Language]
    
    def convert(self, code: str, source_lang: Language, target_lang: Language) -> str:
        """Convert code from source language to target language"""
        if source_lang == target_lang:
            return code  # No conversion needed
        
        # Parse source code into blocks
        blocks = CodeParser.parse_code(code, source_lang)
        
        # Write to target language
        writer = CodeWriter(target_lang)
        result = writer.write_blocks(blocks)
        
        return result
    
    def convert_file(self, source_path: str, target_path: str, 
                     source_lang: Optional[Language] = None,
                     target_lang: Optional[Language] = None) -> bool:
        """Convert a file from one language to another"""
        try:
            source = Path(source_path)
            if not source.exists():
                return False
            
            # Detect languages from extensions if not provided
            if not source_lang:
                source_lang = Language.from_extension(source.suffix)
            
            if not target_lang:
                target_path_obj = Path(target_path)
                target_lang = Language.from_extension(target_path_obj.suffix)
            
            # Read source
            code = source.read_text(encoding='utf-8', errors='replace')
            
            # Convert
            result = self.convert(code, source_lang, target_lang)
            
            # Write output
            target = Path(target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result, encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"Conversion error: {e}")
            return False
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available languages with their extensions"""
        return [
            {"name": "Python", "value": "python", "extensions": ".py"},
            {"name": "JavaScript", "value": "javascript", "extensions": ".js, .jsx"},
            {"name": "TypeScript", "value": "typescript", "extensions": ".ts, .tsx"},
            {"name": "C", "value": "c", "extensions": ".c, .h"},
            {"name": "C++", "value": "cpp", "extensions": ".cpp, .hpp"},
            {"name": "Java", "value": "java", "extensions": ".java"},
            {"name": "C#", "value": "csharp", "extensions": ".cs"},
            {"name": "PHP", "value": "php", "extensions": ".php"},
            {"name": "Ruby", "value": "ruby", "extensions": ".rb"},
            {"name": "Go", "value": "go", "extensions": ".go"},
            {"name": "Rust", "value": "rust", "extensions": ".rs"},
            {"name": "Kotlin", "value": "kotlin", "extensions": ".kt, .kts"},
            {"name": "Swift", "value": "swift", "extensions": ".swift"},
        ]


# Made with Bob