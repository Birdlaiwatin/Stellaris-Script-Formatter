import re
import json
import os
import sys
import random
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox, Toplevel, ttk
from typing import List, Dict

# ---------- 预编译正则表达式（性能优化）----------
RE_GE = re.compile(r'>\s*=')
RE_LE = re.compile(r'<\s*=')
RE_MULTI_SPACE = re.compile(r'\s+')
RE_BRACES = re.compile(r'([{}])')
RE_EQUAL = re.compile(r'(?<![<>])=(?!=)')
RE_LT = re.compile(r'(?<!<)(?<!>)(?<!=)<(?!=)')
RE_GT = re.compile(r'(?<!<)(?<!>)(?<!=)>(?!=)')
RE_STRING_DOUBLE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
RE_STRING_SINGLE = re.compile(r"'([^'\\]*(?:\\.[^'\\]*)*)'")
RE_IDENTIFIER = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
RE_OPERATOR_SPACE = re.compile(r'\s*([=<>!]=?|\+=|-=|\*=|/=|==|!=|>=|<=|>|<)\s*')
RE_BRACKET_SPACE = re.compile(r'\s*([{}[\](),;])\s*')

# ---------- 主题配色（常量）----------
SPACE_BLUE_THEME = {
    "bg": "#0a0f1a", "secondary_bg": "#141e30", "fg": "#d4e6ff", "accent_fg": "#7ab3ff",
    "text_bg": "#1c263b", "text_fg": "#ffffff", "text_border": "#2e3f5e",
    "button_bg": "#1f2b44", "button_fg": "#d4e6ff", "button_hover_bg": "#2a3a5a",
    "button_active_bg": "#314b72", "button_border": "#3f5a8c",
    "primary_button_bg": "#2f5e9e", "primary_button_fg": "#ffffff",
    "primary_button_hover_bg": "#3b6fb8", "primary_button_active_bg": "#4a7fd0",
    "success_button_bg": "#2e7d32", "success_button_fg": "#ffffff",
    "success_button_hover_bg": "#388e3c", "success_button_active_bg": "#43a047",
    "highlight": "#4d7bff", "secondary_highlight": "#7ba6ff",
    "theme_btn_text": "🌌", "theme_btn_hover_bg": "#2a3b5f",
    "settings_btn_text": "⚙️", "settings_btn_hover_bg": "#2a3b5f",
    "header_bg": "#0f1625", "header_fg": "#b0d4ff", "header_border": "#1d2b48",
    "frame_border": "#1d2b48", "scrollbar_bg": "#2e3f5e", "scrollbar_trough": "#1a2538",
    "scrollbar_hover": "#4d7bff", "border": "#2e3f5e",
}
DARK_STAR_THEME = {
    "bg": "#121212", "secondary_bg": "#1e1e1e", "fg": "#e0e0e0", "accent_fg": "#bb86fc",
    "text_bg": "#212121", "text_fg": "#ffffff", "text_border": "#333333",
    "button_bg": "#2d2d2d", "button_fg": "#e0e0e0", "button_hover_bg": "#3a3a3a",
    "button_active_bg": "#4a4a4a", "button_border": "#444444",
    "primary_button_bg": "#6200ee", "primary_button_fg": "#ffffff",
    "primary_button_hover_bg": "#7c4dff", "primary_button_active_bg": "#9d6dff",
    "success_button_bg": "#03dac6", "success_button_fg": "#000000",
    "success_button_hover_bg": "#00e5c3", "success_button_active_bg": "#00f5d4",
    "highlight": "#bb86fc", "secondary_highlight": "#cf9fff",
    "theme_btn_text": "🌃", "theme_btn_hover_bg": "#333333",
    "settings_btn_text": "⚙️", "settings_btn_hover_bg": "#333333",
    "header_bg": "#0a0a0a", "header_fg": "#e0e0e0", "header_border": "#1a1a1a",
    "frame_border": "#333333", "scrollbar_bg": "#333333", "scrollbar_trough": "#1a1a1a",
    "scrollbar_hover": "#6200ee", "border": "#444444",
}
TECH_GREEN_THEME = {
    "bg": "#0a1f0a", "secondary_bg": "#132813", "fg": "#c8ffc8", "accent_fg": "#7dff7d",
    "text_bg": "#1a2e1a", "text_fg": "#ffffff", "text_border": "#2a4a2a",
    "button_bg": "#1e3a1e", "button_fg": "#c8ffc8", "button_hover_bg": "#2a4a2a",
    "button_active_bg": "#3a5a3a", "button_border": "#2a6a2a",
    "primary_button_bg": "#2a7d2a", "primary_button_fg": "#ffffff",
    "primary_button_hover_bg": "#3a8d3a", "primary_button_active_bg": "#4a9d4a",
    "success_button_bg": "#4caf50", "success_button_fg": "#ffffff",
    "success_button_hover_bg": "#5cbf60", "success_button_active_bg": "#6ccf70",
    "highlight": "#4caf50", "secondary_highlight": "#8bc34a",
    "theme_btn_text": "🌿", "theme_btn_hover_bg": "#2a4a2a",
    "settings_btn_text": "⚙️", "settings_btn_hover_bg": "#2a4a2a",
    "header_bg": "#0a1a0a", "header_fg": "#a8ffa8", "header_border": "#1a2a1a",
    "frame_border": "#2a4a2a", "scrollbar_bg": "#2a4a2a", "scrollbar_trough": "#1a2e1a",
    "scrollbar_hover": "#4caf50", "border": "#2a6a2a",
}
DAWN_WHITE_THEME = {
    "bg": "#fdf5e6", "secondary_bg": "#fff2df", "fg": "#5d4e3d", "accent_fg": "#ffb347",
    "text_bg": "#ffffff", "text_fg": "#5d4e3d", "text_border": "#d2b48c",
    "button_bg": "#f0e0c0", "button_fg": "#5d4e3d", "button_hover_bg": "#e6d0a0",
    "button_active_bg": "#d2b48c", "button_border": "#c4a484",
    "primary_button_bg": "#ff8c42", "primary_button_fg": "#ffffff",
    "primary_button_hover_bg": "#ff9f5c", "primary_button_active_bg": "#e67e22",
    "success_button_bg": "#8bc34a", "success_button_fg": "#ffffff",
    "success_button_hover_bg": "#9ccc65", "success_button_active_bg": "#7cb342",
    "highlight": "#ffb347", "secondary_highlight": "#ffcc80",
    "theme_btn_text": "☀️", "theme_btn_hover_bg": "#e6d0a0",
    "settings_btn_text": "⚙️", "settings_btn_hover_bg": "#e6d0a0",
    "header_bg": "#fff2df", "header_fg": "#5d4e3d", "header_border": "#d2b48c",
    "frame_border": "#d2b48c", "scrollbar_bg": "#d2b48c", "scrollbar_trough": "#f0e0c0",
    "scrollbar_hover": "#ff8c42", "border": "#c4a484",
}
MINIMAL_GRAY_THEME = {
    "bg": "#e6f0fa", "secondary_bg": "#ffffff", "fg": "#2c3e50", "accent_fg": "#4aa3df",
    "text_bg": "#ffffff", "text_fg": "#2c3e50", "text_border": "#b0bec5",
    "button_bg": "#e0e5ec", "button_fg": "#2c3e50", "button_hover_bg": "#d0d9e8",
    "button_active_bg": "#c0c9d8", "button_border": "#90a4ae",
    "primary_button_bg": "#4aa3df", "primary_button_fg": "#ffffff",
    "primary_button_hover_bg": "#5eb6f0", "primary_button_active_bg": "#3b8fc2",
    "success_button_bg": "#66bb6a", "success_button_fg": "#ffffff",
    "success_button_hover_bg": "#7ecb7f", "success_button_active_bg": "#4caf50",
    "highlight": "#4aa3df", "secondary_highlight": "#7fc5f0",
    "theme_btn_text": "🌤️", "theme_btn_hover_bg": "#d0d9e8",
    "settings_btn_text": "⚙️", "settings_btn_hover_bg": "#d0d9e8",
    "header_bg": "#ffffff", "header_fg": "#2c3e50", "header_border": "#b0bec5",
    "frame_border": "#b0bec5", "scrollbar_bg": "#b0bec5", "scrollbar_trough": "#e0e5ec",
    "scrollbar_hover": "#4aa3df", "border": "#90a4ae",
}

THEME_DICT = {
    "space_blue": SPACE_BLUE_THEME,
    "dark_star": DARK_STAR_THEME,
    "tech_green": TECH_GREEN_THEME,
    "dawn_white": DAWN_WHITE_THEME,
    "minimal_gray": MINIMAL_GRAY_THEME,
}
THEME_DISPLAY_NAMES = {
    "space_blue": "🌌 太空蓝 (深色)",
    "dark_star": "🌃 暗夜星辰 (深色)",
    "tech_green": "🌿 科技绿 (深色)",
    "dawn_white": "☀️ 晨曦白 (浅色)",
    "minimal_gray": "🌤️ 极简灰 (浅色)",
}
DEFAULT_SETTINGS = {
    "output_mode": False,
    "output_file_path": "",
    "theme": "space_blue",
    "simplify_max_1000": False,   # 新增复选框状态
}

# ---------- 工具函数 ----------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')

def load_settings() -> Dict:
    settings = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for key in DEFAULT_SETTINGS:
                    if key in loaded:
                        settings[key] = loaded[key]
        except Exception as e:
            print(f"加载设置出错: {e}")
    if settings["theme"] not in THEME_DICT:
        settings["theme"] = DEFAULT_SETTINGS["theme"]
    return settings

def save_settings(settings: Dict):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存设置出错: {e}")

# ---------- 自定义滚动条（每个实例独立样式）----------
class AppScrollbar(ttk.Scrollbar):
    _instances = []  # 存储所有实例，用于主题切换时统一更新

    def __init__(self, master=None, **kwargs):
        self._style_name = f"CustomScrollbar_{id(self)}"
        # 先创建样式，再调用父类初始化，避免 Layout not found
        style = ttk.Style()
        # 创建元素
        style.element_create(f"{self._style_name}.trough", "from", "clam")
        style.element_create(f"{self._style_name}.thumb", "from", "clam")
        # 定义布局
        style.layout(self._style_name, [
            (f"{self._style_name}.trough", {
                'sticky': 'nswe',
                'children': [
                    (f"{self._style_name}.thumb", {
                        'unit': '1',
                        'sticky': 'nswe'
                    })
                ]
            })
        ])
        # 默认颜色（稍后会被主题覆盖）
        style.configure(self._style_name,
            background="gray",
            troughcolor="gray",
            bordercolor="gray",
            lightcolor="gray",
            darkcolor="gray",
            arrowcolor="black",
            relief="flat"
        )
        style.map(self._style_name,
            background=[('active', "lightgray")]
        )

        super().__init__(master, style=self._style_name, **kwargs)
        self._instances.append(self)

    def apply_theme(self, theme_colors: Dict):
        """更新滚动条颜色"""
        style = ttk.Style()
        style.configure(self._style_name,
            background=theme_colors["scrollbar_bg"],
            troughcolor=theme_colors["scrollbar_trough"],
            bordercolor=theme_colors["border"],
            lightcolor=theme_colors["border"],
            darkcolor=theme_colors["border"],
            arrowcolor=theme_colors["fg"],
            relief="flat"
        )
        style.map(self._style_name,
            background=[('active', theme_colors["scrollbar_hover"])]
        )

    @classmethod
    def update_all_themes(cls, theme_colors: Dict):
        """更新所有已存在的滚动条样式"""
        for instance in cls._instances:
            if instance.winfo_exists():
                instance.apply_theme(theme_colors)

# ---------- 带滚动条的文本框 ----------
class ScrollableText(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master)
        self.text = tk.Text(self, wrap="word", **kwargs)
        self.v_scrollbar = AppScrollbar(self, orient=tk.VERTICAL)
        self.text.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.configure(command=self.text.yview)

        self.text.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 鼠标滚轮支持
        def on_mousewheel(event):
            if event.num == 4 or event.delta > 0:
                self.text.yview_scroll(-1, "units")
            else:
                self.text.yview_scroll(1, "units")
            return "break"
        self.text.bind("<MouseWheel>", on_mousewheel)
        self.text.bind("<Button-4>", on_mousewheel)
        self.text.bind("<Button-5>", on_mousewheel)

    def update_theme(self, theme_colors: Dict):
        self.text.configure(
            bg=theme_colors["text_bg"],
            fg=theme_colors["text_fg"],
            insertbackground=theme_colors["text_fg"],
            selectbackground=theme_colors["secondary_highlight"],
            selectforeground=theme_colors["text_fg"],
            highlightbackground=theme_colors["text_border"],
            highlightcolor=theme_colors["highlight"]
        )

    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)

    def bind(self, *args, **kwargs):
        return self.text.bind(*args, **kwargs)

# ---------- 悬停按钮 ----------
class HoverButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        self.hover_bg = kwargs.pop('hover_bg', None)
        self.hover_fg = kwargs.pop('hover_fg', None)
        tk.Button.__init__(self, master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.default_bg = self.cget("bg")
        self.default_fg = self.cget("fg")
        if self.hover_bg is None:
            self.hover_bg = self.default_bg
        if self.hover_fg is None:
            self.hover_fg = self.default_fg

    def on_enter(self, e):
        if self.cget("state") != "disabled":
            self.configure(bg=self.hover_bg, fg=self.hover_fg)

    def on_leave(self, e):
        if self.cget("state") != "disabled":
            self.configure(bg=self.default_bg, fg=self.default_fg)

    def update_hover_colors(self, hover_bg=None, hover_fg=None):
        if hover_bg is not None:
            self.hover_bg = hover_bg
        if hover_fg is not None:
            self.hover_fg = hover_fg

# ---------- 核心格式化函数 ----------
def format_stellaris_script(text: str) -> str:
    text = RE_GE.sub('>=', text)
    text = RE_LE.sub('<=', text)
    text = ' '.join(text.split())
    text = RE_BRACES.sub(r' \1 ', text)
    text = RE_EQUAL.sub(r' = ', text)
    text = RE_LT.sub(r' < ', text)
    text = RE_GT.sub(r' > ', text)
    text = ' '.join(text.split())
    tokens = text.split()
    if not tokens:
        return ""

    result: List[str] = []
    indent = 0
    i = 0
    last_was_closing_brace = False

    while i < len(tokens):
        token = tokens[i]
        if token == '{':
            if result and result[-1].endswith('\n'):
                result[-1] = result[-1].rstrip('\n').rstrip() + ' {\n'
            else:
                result.append(' {\n')
            indent += 1
            last_was_closing_brace = False
            i += 1
            continue
        if token == '}':
            indent = max(0, indent - 1)
            if last_was_closing_brace and indent > 0:
                remaining = ' '.join(tokens[i+1:]).strip()
                if remaining and not remaining.startswith('}'):
                    result.append('\n')
            result.append('    ' * indent + '}\n')
            last_was_closing_brace = True
            i += 1
            continue
        if i + 1 < len(tokens) and tokens[i + 1] in {'=', '>=', '<=', '<', '>'}:
            key = token
            operator = tokens[i + 1]
            i += 2
            value_parts = []
            while i < len(tokens):
                if tokens[i] in {'{', '}'} or (i + 1 < len(tokens) and tokens[i + 1] in {'=', '>=', '<=', '<', '>'}):
                    break
                value_parts.append(tokens[i])
                i += 1
            value = ' '.join(value_parts).strip()
            line = '    ' * indent + f"{key} {operator} {value}"
            result.append(line + '\n')
            last_was_closing_brace = False
            if i < len(tokens) and tokens[i] == '{':
                continue
        else:
            result.append('    ' * indent + token + '\n')
            last_was_closing_brace = False
            i += 1

    output = ''.join(result).rstrip('\n')
    output = re.sub(r'\n{3,}', '\n\n', output)
    return output.rstrip() + '\n'

def remove_comments_and_format_block(block_lines: list[str]) -> str:
    processed_lines = []
    str_counter = 0
    str_map = {}
    for line in block_lines:
        line = line.split('#', 1)[0].rstrip()
        if not line.strip():
            continue
        def protect_str(match):
            nonlocal str_counter
            placeholder = f"__STR_{str_counter}__"
            str_map[placeholder] = match.group(0)
            str_counter += 1
            return placeholder
        line = RE_STRING_DOUBLE.sub(protect_str, line)
        line = RE_STRING_SINGLE.sub(protect_str, line)
        processed_lines.append(line)
    if not processed_lines:
        return ""
    result = ' '.join(processed_lines)
    identifiers = set(RE_IDENTIFIER.findall(result))
    underscore_protected = {}
    for i, word in enumerate(identifiers):
        if '_' in word and word not in str_map.values():
            placeholder = f"__ID_{i}__"
            underscore_protected[placeholder] = word
            result = result.replace(word, placeholder)
    result = ' '.join(result.split())
    result = RE_OPERATOR_SPACE.sub(r' \1 ', result)
    result = RE_BRACKET_SPACE.sub(r'\1 ', result)
    result = ' '.join(result.split())
    for ph, original in underscore_protected.items():
        result = result.replace(ph, original)
    for ph, original in str_map.items():
        result = result.replace(ph, original)
    return result.strip()

def compact_stellaris_script(text: str) -> str:
    lines = text.splitlines()
    blocks = []
    current_block = []
    brace_depth = 0
    in_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if not stripped:
            if in_block and current_block:
                current_block.append('')
            continue
        open_braces = line.count('{')
        close_braces = line.count('}')
        if not in_block and open_braces > 0:
            in_block = True
            brace_depth = open_braces - close_braces
        else:
            brace_depth += open_braces - close_braces
        current_block.append(line)
        if in_block and brace_depth <= 0:
            formatted = remove_comments_and_format_block(current_block)
            if formatted:
                blocks.append(formatted)
            current_block = []
            in_block = False
            brace_depth = 0
    if current_block:
        formatted = remove_comments_and_format_block(current_block)
        if formatted:
            blocks.append(formatted)
    return '\n'.join(blocks)

# ---------- 简化函数 ----------
def simplify_output(text: str) -> str:
    """对紧凑结果进一步简化：删除运算符两边空格（仅当两边都有空格），并移除大括号周围多余空格"""
    # 1. 删除运算符两边的空格（仅当两边都有非空格字符）
    text = re.sub(r'(?<=\S)\s+([=<>!]=?)\s+(?=\S)', r'\1', text)
    # 2. 删除 { 前面的空格（例如 " = {" -> "={"）
    text = re.sub(r'\s+{', '{', text)
    # 3. 删除 { 后面的空格（例如 "{ " -> "{"）
    text = re.sub(r'{\s+', '{', text)
    # 4. 删除 } 前面的空格（例如 " }" -> "}"）
    text = re.sub(r'\s+}', '}', text)
    # 5. 删除 } 后面的空格（例如 "} " -> "}"）
    text = re.sub(r'}\s+', '}', text)
    return text

# ---------- 主应用程序类 ----------
class StellarisFormatterApp:
    def __init__(self):
        self.settings = load_settings()
        self.current_theme_key = self.settings["theme"]
        self.theme = THEME_DICT[self.current_theme_key].copy()

        self.root = tk.Tk()
        self.root.title("Stellaris 脚本转换工具 v1.5")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)
        self.root.configure(bg=self.theme["bg"])

        # 创建界面组件
        self._create_header()
        self._create_input_area()
        self._create_button_area()
        self._create_output_area()
        self._create_footer()

        # 应用主题（确保所有控件颜色正确）
        self._apply_theme()

    def _create_header(self):
        """创建标题栏"""
        header_frame = tk.Frame(
            self.root,
            bg=self.theme["header_bg"],
            highlightbackground=self.theme["header_border"],
            highlightthickness=1
        )
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        title_label = tk.Label(
            header_frame,
            text="Stellaris 脚本转换工具",
            anchor="w",
            bg=self.theme["header_bg"],
            fg=self.theme["header_fg"],
            font=("微软雅黑", 12, "bold")
        )
        title_label.pack(side="left", padx=15, pady=10)

        label_input = tk.Label(
            header_frame,
            text="输入原始脚本：",
            anchor="w",
            bg=self.theme["header_bg"],
            fg=self.theme["header_fg"],
            font=("微软雅黑", 10)
        )
        label_input.pack(side="left", padx=(20, 0))

        # 主题切换按钮
        self.theme_btn = HoverButton(
            header_frame,
            text=self.theme["theme_btn_text"],
            command=self.toggle_theme,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["theme_btn_hover_bg"],
            font=("Segoe UI", 12),
            width=3,
            bd=2,
            relief="raised"
        )
        self.theme_btn.pack(side="right", padx=5, pady=5)

        # 设置按钮
        self.settings_btn = HoverButton(
            header_frame,
            text=self.theme["settings_btn_text"],
            command=self.open_settings,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["settings_btn_hover_bg"],
            font=("Segoe UI", 12),
            width=3,
            bd=2,
            relief="raised"
        )
        self.settings_btn.pack(side="right", padx=5, pady=5)

        # 输出模式按钮
        self.output_mode_btn = HoverButton(
            header_frame,
            text="",
            command=self.toggle_output_mode,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["button_hover_bg"],
            font=("微软雅黑", 9),
            bd=2,
            relief="raised",
            padx=10
        )
        self.output_mode_btn.pack(side="right", padx=(0, 5), pady=5)
        self._update_output_mode_button()

        # 保存引用以便主题切换时更新
        self.header_frame = header_frame
        self.title_label = title_label
        self.label_input = label_input

    def _create_input_area(self):
        """创建输入区域"""
        input_frame = tk.Frame(
            self.root,
            bg=self.theme["secondary_bg"],
            highlightbackground=self.theme["frame_border"],
            highlightthickness=1,
            height=200
        )
        input_frame.pack(fill="x", padx=10, pady=5)
        input_frame.pack_propagate(False)

        self.input_textbox = ScrollableText(
            input_frame,
            font=("Consolas", 11)
        )
        self.input_textbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.input_frame = input_frame

    def _create_button_area(self):
        """创建按钮区域（含复选框）"""
        btn_frame = tk.Frame(
            self.root,
            bg=self.theme["secondary_bg"],
            highlightbackground=self.theme["frame_border"],
            highlightthickness=1
        )
        btn_frame.pack(pady=10, padx=10, fill="x")

        # 使用grid布局，两列放置按钮，第三行放置复选框
        btn_frame.grid_rowconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_to_formatted = HoverButton(
            btn_frame,
            text="指令格式化 ⬅",
            command=self.to_formatted,
            bg=self.theme["primary_button_bg"],
            fg=self.theme["primary_button_fg"],
            activebackground=self.theme["primary_button_active_bg"],
            hover_bg=self.theme["primary_button_hover_bg"],
            font=("微软雅黑", 10, "bold"),
            height=1,
            bd=3,
            relief="raised",
            padx=20,
            pady=8
        )
        self.btn_to_formatted.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.btn_to_compact = HoverButton(
            btn_frame,
            text="➡ 转化为指令",
            command=self.to_compact,
            bg=self.theme["primary_button_bg"],
            fg=self.theme["primary_button_fg"],
            activebackground=self.theme["primary_button_active_bg"],
            hover_bg=self.theme["primary_button_hover_bg"],
            font=("微软雅黑", 10, "bold"),
            height=1,
            bd=3,
            relief="raised",
            padx=20,
            pady=8
        )
        self.btn_to_compact.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # 复选框框架
        self.check_frame = tk.Frame(btn_frame, bg=self.theme["secondary_bg"])
        self.check_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        self.simplify_var = tk.BooleanVar(value=self.settings.get("simplify_max_1000", False))
        self.simplify_check = tk.Checkbutton(
            self.check_frame,
            text="最简化（控制台最多输入1000字符）",
            variable=self.simplify_var,
            command=self._toggle_simplify,
            bg=self.theme["secondary_bg"],
            fg=self.theme["fg"],
            selectcolor=self.theme["secondary_bg"],
            activebackground=self.theme["secondary_bg"]
        )
        self.simplify_check.pack(anchor="center")

        self.btn_frame = btn_frame

    def _toggle_simplify(self):
        """复选框状态变更时保存设置"""
        self.settings["simplify_max_1000"] = self.simplify_var.get()
        save_settings(self.settings)

    def _create_output_area(self):
        """创建输出区域（含字符数显示）"""
        self.output_frame = tk.Frame(
            self.root,
            bg=self.theme["secondary_bg"],
            highlightbackground=self.theme["frame_border"],
            highlightthickness=1
        )
        self.output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 顶部框架：左边标签，右边字符数
        self.output_header = tk.Frame(self.output_frame, bg=self.theme["secondary_bg"])
        self.output_header.pack(fill="x", padx=10, pady=(5, 0))

        self.label_output = tk.Label(
            self.output_header,
            text="转换结果：",
            anchor="w",
            bg=self.theme["secondary_bg"],
            fg=self.theme["accent_fg"],
            font=("微软雅黑", 10, "bold")
        )
        self.label_output.pack(side="left")

        self.char_count_label = tk.Label(
            self.output_header,
            text="字符数: 0",
            anchor="e",
            bg=self.theme["secondary_bg"],
            fg=self.theme["fg"],
            font=("微软雅黑", 9)
        )
        self.char_count_label.pack(side="right")

        # 文本框
        self.output_textbox = ScrollableText(
            self.output_frame,
            font=("Consolas", 11)
        )
        self.output_textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def _create_footer(self):
        """创建底部版本信息"""
        self.version_label = tk.Label(
            self.root,
            text="v1.5 | 专为《群星》脚本转换格式设计",
            anchor="center",
            bg=self.theme["bg"],
            fg=self.theme["fg"],
            font=("微软雅黑", 8)
        )
        self.version_label.pack(fill="x", pady=(5, 10))

    def _apply_theme(self):
        """应用当前主题到所有界面元素"""
        t = self.theme
        self.root.configure(bg=t["bg"])

        # 标题栏
        self.header_frame.configure(bg=t["header_bg"], highlightbackground=t["header_border"])
        self.title_label.configure(bg=t["header_bg"], fg=t["header_fg"])
        self.label_input.configure(bg=t["header_bg"], fg=t["header_fg"])

        # 主题按钮
        self.theme_btn.configure(
            text=t["theme_btn_text"],
            bg=t["button_bg"],
            fg=t["button_fg"],
            activebackground=t["button_active_bg"]
        )
        self.theme_btn.default_bg = t["button_bg"]
        self.theme_btn.default_fg = t["button_fg"]
        self.theme_btn.update_hover_colors(hover_bg=t["theme_btn_hover_bg"])

        # 设置按钮
        self.settings_btn.configure(
            text=t["settings_btn_text"],
            bg=t["button_bg"],
            fg=t["button_fg"],
            activebackground=t["button_active_bg"]
        )
        self.settings_btn.default_bg = t["button_bg"]
        self.settings_btn.default_fg = t["button_fg"]
        self.settings_btn.update_hover_colors(hover_bg=t["settings_btn_hover_bg"])

        # 输出模式按钮（颜色可能因模式不同而不同，调用专用方法）
        self._update_output_mode_button()

        # 输入区域
        self.input_frame.configure(bg=t["secondary_bg"], highlightbackground=t["frame_border"])
        self.input_textbox.update_theme(t)

        # 按钮区域
        self.btn_frame.configure(bg=t["secondary_bg"], highlightbackground=t["frame_border"])
        self.check_frame.configure(bg=t["secondary_bg"])
        self.simplify_check.configure(bg=t["secondary_bg"], fg=t["fg"], selectcolor=t["secondary_bg"],
                                       activebackground=t["secondary_bg"])

        # 主按钮
        self.btn_to_formatted.configure(
            bg=t["primary_button_bg"],
            fg=t["primary_button_fg"],
            activebackground=t["primary_button_active_bg"]
        )
        self.btn_to_formatted.default_bg = t["primary_button_bg"]
        self.btn_to_formatted.default_fg = t["primary_button_fg"]
        self.btn_to_formatted.update_hover_colors(hover_bg=t["primary_button_hover_bg"])

        self.btn_to_compact.configure(
            bg=t["primary_button_bg"],
            fg=t["primary_button_fg"],
            activebackground=t["primary_button_active_bg"]
        )
        self.btn_to_compact.default_bg = t["primary_button_bg"]
        self.btn_to_compact.default_fg = t["primary_button_fg"]
        self.btn_to_compact.update_hover_colors(hover_bg=t["primary_button_hover_bg"])

        # 输出区域
        self.output_frame.configure(bg=t["secondary_bg"], highlightbackground=t["frame_border"])
        self.output_header.configure(bg=t["secondary_bg"])
        self.label_output.configure(bg=t["secondary_bg"], fg=t["accent_fg"])
        self.char_count_label.configure(bg=t["secondary_bg"], fg=t["fg"])
        self.output_textbox.update_theme(t)

        # 版本标签
        self.version_label.configure(bg=t["bg"], fg=t["fg"])

        # 更新所有滚动条样式
        AppScrollbar.update_all_themes(t)

    def _update_output_mode_button(self):
        """更新输出模式按钮的样式和文字"""
        t = self.theme
        if self.settings["output_mode"]:
            self.output_mode_btn.configure(
                text="📁 文件输出",
                bg=t["success_button_bg"],
                fg=t["success_button_fg"],
                activebackground=t["success_button_active_bg"]
            )
            self.output_mode_btn.default_bg = t["success_button_bg"]
            self.output_mode_btn.default_fg = t["success_button_fg"]
            self.output_mode_btn.update_hover_colors(hover_bg=t["success_button_hover_bg"])
        else:
            self.output_mode_btn.configure(
                text="📄 界面输出",
                bg=t["button_bg"],
                fg=t["button_fg"],
                activebackground=t["button_active_bg"]
            )
            self.output_mode_btn.default_bg = t["button_bg"]
            self.output_mode_btn.default_fg = t["button_fg"]
            self.output_mode_btn.update_hover_colors(hover_bg=t["button_hover_bg"])

    def toggle_theme(self):
        """随机切换主题"""
        themes = list(THEME_DICT.keys())
        new_theme_key = random.choice(themes)
        if new_theme_key == self.current_theme_key:
            # 相同主题不重复切换，但可以重新应用
            pass
        self.current_theme_key = new_theme_key
        self.theme.clear()
        self.theme.update(THEME_DICT[self.current_theme_key])
        self.settings["theme"] = self.current_theme_key
        save_settings(self.settings)
        self._apply_theme()

    def toggle_output_mode(self):
        self.settings["output_mode"] = not self.settings["output_mode"]
        self._update_output_mode_button()
        save_settings(self.settings)

    def _update_char_count(self, text: str):
        """更新字符数显示"""
        count = len(text)
        self.char_count_label.config(text=f"字符数: {count}")

    def _handle_output(self, result_text: str, operation_name: str):
        """根据输出模式处理结果（不包含字符数更新，字符数在调用前更新）"""
        if self.settings["output_mode"] and self.settings["output_file_path"]:
            try:
                out_dir = os.path.dirname(self.settings["output_file_path"])
                if out_dir and not os.path.exists(out_dir):
                    os.makedirs(out_dir, exist_ok=True)
                with open(self.settings["output_file_path"], 'w', encoding='utf-8') as f:
                    f.write(result_text)
                self.output_textbox.delete("1.0", tk.END)
                self.output_textbox.insert(tk.END, f"✓ {operation_name} 结果已保存至文件：\n{self.settings['output_file_path']}")
                self.output_textbox.text.tag_config("success", foreground="#4CAF50", font=("Consolas", 11, "bold"))
                self.output_textbox.text.tag_add("success", "1.0", "1.1")
            except Exception as e:
                self.output_textbox.delete("1.0", tk.END)
                self.output_textbox.insert(tk.END, f"❌ 写入文件失败：{e}\n\n结果将显示在此：\n{result_text}")
                self.output_textbox.text.tag_config("error", foreground="#f44336", font=("Consolas", 11, "bold"))
                self.output_textbox.text.tag_add("error", "1.0", "1.1")
        else:
            self.output_textbox.delete("1.0", tk.END)
            self.output_textbox.insert(tk.END, result_text)

    def to_formatted(self):
        input_text = self.input_textbox.get("1.0", tk.END).strip()
        if not input_text:
            self.output_textbox.delete("1.0", tk.END)
            self.output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
            return
        try:
            result = format_stellaris_script(input_text)
            self._update_char_count(result)
            self._handle_output(result, "指令格式化")
        except Exception as e:
            self.output_textbox.delete("1.0", tk.END)
            self.output_textbox.insert(tk.END, f"格式化出错：{e}")
            self.output_textbox.text.tag_add("error", "1.0", "1.1")

    def to_compact(self):
        input_text = self.input_textbox.get("1.0", tk.END).strip()
        if not input_text:
            self.output_textbox.delete("1.0", tk.END)
            self.output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
            return
        try:
            result = compact_stellaris_script(input_text)
            # 如果复选框选中，进一步简化结果
            if self.simplify_var.get():
                result = simplify_output(result)
            self._update_char_count(result)
            self._handle_output(result, "转化为指令")
        except Exception as e:
            self.output_textbox.delete("1.0", tk.END)
            self.output_textbox.insert(tk.END, f"转换出错：{e}")
            self.output_textbox.text.tag_add("error", "1.0", "1.1")

    def open_settings(self):
        """打开设置窗口"""
        settings_win = Toplevel(self.root)
        settings_win.title("设置")
        settings_win.resizable(False, False)
        settings_win.configure(bg=self.theme["secondary_bg"])
        settings_win.transient(self.root)
        settings_win.grab_set()

        win_width, win_height = 550, 480
        settings_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (win_width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (win_height // 2)
        settings_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # 标题栏
        title_frame = tk.Frame(settings_win, bg=self.theme["header_bg"], height=40)
        title_frame.pack(fill="x", pady=(0, 10))
        title_frame.pack_propagate(False)
        tk.Label(
            title_frame,
            text="Stellaris 脚本转换工具 - 设置",
            bg=self.theme["header_bg"],
            fg=self.theme["header_fg"],
            font=("微软雅黑", 12, "bold")
        ).pack(expand=True)

        # 版本信息
        version_frame = tk.Frame(settings_win, bg=self.theme["secondary_bg"])
        version_frame.pack(fill="x", pady=(5, 10), padx=20)
        tk.Label(
            version_frame,
            text="当前版本：1.5",
            bg=self.theme["secondary_bg"],
            fg=self.theme["fg"],
            font=("微软雅黑", 10)
        ).pack(side="left")

        # 主题选择
        theme_frame = tk.Frame(settings_win, bg=self.theme["secondary_bg"])
        theme_frame.pack(pady=5, padx=20, fill="x")
        tk.Label(
            theme_frame,
            text="主题选择：",
            bg=self.theme["secondary_bg"],
            fg=self.theme["fg"],
            font=("微软雅黑", 9)
        ).pack(anchor="w")

        theme_select_frame = tk.Frame(theme_frame, bg=self.theme["secondary_bg"])
        theme_select_frame.pack(fill="x", pady=5)

        theme_var = tk.StringVar(value=THEME_DISPLAY_NAMES[self.current_theme_key])

        def on_theme_change(*args):
            selected_display = theme_var.get()
            for key, display in THEME_DISPLAY_NAMES.items():
                if display == selected_display:
                    if key != self.current_theme_key:
                        self.current_theme_key = key
                        self.theme.clear()
                        self.theme.update(THEME_DICT[self.current_theme_key])
                        self.settings["theme"] = self.current_theme_key
                        save_settings(self.settings)
                        self._apply_theme()
                    break

        theme_menu = tk.OptionMenu(
            theme_select_frame,
            theme_var,
            *THEME_DISPLAY_NAMES.values(),
            command=lambda _: on_theme_change()
        )
        theme_menu.config(
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            activeforeground=self.theme["button_fg"],
            font=("微软雅黑", 9),
            bd=2,
            relief="raised"
        )
        theme_menu.pack(side="left", fill="x", expand=True)

        # 文件路径设置
        path_frame = tk.Frame(settings_win, bg=self.theme["secondary_bg"])
        path_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(
            path_frame,
            text="输出文件路径：",
            bg=self.theme["secondary_bg"],
            fg=self.theme["fg"],
            font=("微软雅黑", 9)
        ).pack(anchor="w")

        path_input_frame = tk.Frame(path_frame, bg=self.theme["secondary_bg"])
        path_input_frame.pack(fill="x", pady=5)

        temp_path_var = tk.StringVar(value=self.settings["output_file_path"])

        path_entry = tk.Entry(
            path_input_frame,
            textvariable=temp_path_var,
            bg=self.theme["text_bg"],
            fg=self.theme["text_fg"],
            insertbackground=self.theme["text_fg"],
            font=("Consolas", 9),
            bd=2,
            relief="sunken",
            highlightbackground=self.theme["text_border"],
            highlightcolor=self.theme["highlight"],
            highlightthickness=1
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse_file():
            file_path = filedialog.asksaveasfilename(
                title="选择输出文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                temp_path_var.set(file_path)
                self.settings["output_file_path"] = file_path
                save_settings(self.settings)

        browse_btn = HoverButton(
            path_input_frame,
            text="浏览",
            command=browse_file,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["button_hover_bg"],
            font=("微软雅黑", 9),
            relief="raised",
            bd=2,
            padx=15,
            pady=3
        )
        browse_btn.pack(side="left", padx=(0, 5))

        def save_settings_and_close():
            self.settings["output_file_path"] = temp_path_var.get()
            save_settings(self.settings)
            settings_win.destroy()

        save_btn = HoverButton(
            path_input_frame,
            text="保存设置",
            command=save_settings_and_close,
            bg=self.theme["primary_button_bg"],
            fg=self.theme["primary_button_fg"],
            activebackground=self.theme["primary_button_active_bg"],
            hover_bg=self.theme["primary_button_hover_bg"],
            font=("微软雅黑", 9, "bold"),
            relief="raised",
            bd=2,
            padx=15,
            pady=3
        )
        save_btn.pack(side="left")

        # 分隔线
        separator = tk.Frame(settings_win, bg=self.theme["border"], height=2)
        separator.pack(fill=tk.X, padx=20, pady=15)

        # 垂直按钮区域
        vertical_btn_frame = tk.Frame(settings_win, bg=self.theme["secondary_bg"])
        vertical_btn_frame.pack(pady=20, padx=20, fill="x")

        def check_update():
            webbrowser.open("https://github.com/Birdlaiwatin/Stellaris-Script-Formatter")
            messagebox.showinfo("检查更新", "已为您打开项目主页，请查看最新版本。")

        check_btn = HoverButton(
            vertical_btn_frame,
            text="检查更新",
            command=check_update,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["button_hover_bg"],
            font=("微软雅黑", 10),
            relief="raised",
            bd=2,
            width=20,
            padx=10,
            pady=5
        )
        check_btn.pack(pady=3)

        def show_about():
            about_win = Toplevel(settings_win)
            about_win.title("关于")
            about_win.resizable(False, False)
            about_win.configure(bg=self.theme["secondary_bg"])
            about_win.transient(settings_win)
            about_win.grab_set()
            about_win.update_idletasks()
            x = settings_win.winfo_x() + (settings_win.winfo_width() // 2) - 200
            y = settings_win.winfo_y() + (settings_win.winfo_height() // 2) - 150
            about_win.geometry(f"400x250+{x}+{y}")
            tk.Label(
                about_win,
                text="Stellaris 脚本转换工具\n\n"
                     "版本 1.5\n\n"
                     "专为《群星》脚本转换格式设计\n\n",
                bg=self.theme["secondary_bg"],
                fg=self.theme["fg"],
                font=("微软雅黑", 10),
                justify="center"
            ).pack(expand=True, pady=20)
            close_about_btn = HoverButton(
                about_win,
                text="关闭",
                command=about_win.destroy,
                bg=self.theme["primary_button_bg"],
                fg=self.theme["primary_button_fg"],
                activebackground=self.theme["primary_button_active_bg"],
                hover_bg=self.theme["primary_button_hover_bg"],
                font=("微软雅黑", 9),
                relief="raised",
                bd=2,
                width=10
            )
            close_about_btn.pack(pady=10)

        about_btn = HoverButton(
            vertical_btn_frame,
            text="关于",
            command=show_about,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["button_hover_bg"],
            font=("微软雅黑", 10),
            relief="raised",
            bd=2,
            width=20,
            padx=10,
            pady=5
        )
        about_btn.pack(pady=3)

        close_btn = HoverButton(
            vertical_btn_frame,
            text="关闭",
            command=settings_win.destroy,
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["button_active_bg"],
            hover_bg=self.theme["button_hover_bg"],
            font=("微软雅黑", 10),
            relief="raised",
            bd=2,
            width=20,
            padx=10,
            pady=5
        )
        close_btn.pack(pady=3)

    def run(self):
        self.root.mainloop()

# ---------- 程序入口 ----------
if __name__ == "__main__":
    app = StellarisFormatterApp()
    app.run()