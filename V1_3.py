import re
import json
import os
import sys
import random
import tkinter as tk
import webbrowser  # 新增：用于打开链接
from tkinter import scrolledtext, filedialog, messagebox, Toplevel, ttk
from typing import List

# ---------- 预编译正则表达式（性能优化）----------
RE_GE = re.compile(r'>\s*=')
RE_LE = re.compile(r'<\s*=')
RE_MULTI_SPACE = re.compile(r'\s+')
RE_BRACES = re.compile(r'([{}])')
RE_EQUAL = re.compile(r'(?<![<>])=(?!=)')
RE_LT = re.compile(r'(?<!<)(?<!>)(?<!=)<(?!=)')
RE_GT = re.compile(r'(?<!<)(?<!>)(?<!=)>(?!=)')

# 用于 compact 操作
RE_STRING_DOUBLE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
RE_STRING_SINGLE = re.compile(r"'([^'\\]*(?:\\.[^'\\]*)*)'")
RE_IDENTIFIER = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')
RE_OPERATOR_SPACE = re.compile(r'\s*([=<>!]=?|\+=|-=|\*=|/=|==|!=|>=|<=|>|<)\s*')
RE_BRACKET_SPACE = re.compile(r'\s*([{}[\](),;])\s*')

# ---------- 获取程序所在目录（兼容脚本和exe）----------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')

# ---------- 默认设置（移除 text_wrap）----------
DEFAULT_SETTINGS = {
    "output_mode": False,          # False=输出到界面，True=输出到文件
    "output_file_path": "",         # 默认空，需要用户设置
    "theme": "space_blue"           # 默认太空蓝主题
}

# 全局设置变量
settings = DEFAULT_SETTINGS.copy()

# ---------- 加载/保存设置 ----------
def load_settings():
    global settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # 只更新存在的键，避免缺少字段
                for key in DEFAULT_SETTINGS:
                    if key in loaded:
                        settings[key] = loaded[key]
        except Exception as e:
            print(f"加载设置出错: {e}")
    
    # 确保主题设置是有效的
    valid_themes = ["space_blue", "dark_star", "tech_green", "dawn_white", "minimal_gray"]
    if settings["theme"] not in valid_themes:
        settings["theme"] = DEFAULT_SETTINGS["theme"]

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存设置出错: {e}")

# 初始加载
load_settings()

# ---------- 美化后的主题配色（微调颜色值，使对比更柔和）----------
# 太空蓝主题（主色调）
SPACE_BLUE_THEME = {
    "bg": "#0a0f1a",                # 稍亮一点的深空背景
    "secondary_bg": "#141e30",      # 次级背景
    "fg": "#d4e6ff",                # 字体更柔和
    "accent_fg": "#7ab3ff",          # 强调色
    "text_bg": "#1c263b",            # 文本框背景
    "text_fg": "#ffffff",            # 文本框字体
    "text_border": "#2e3f5e",        # 文本框边框
    "button_bg": "#1f2b44",           # 按钮背景
    "button_fg": "#d4e6ff",           # 按钮字体
    "button_hover_bg": "#2a3a5a",     # 按钮悬停背景
    "button_active_bg": "#314b72",    # 按钮激活背景
    "button_border": "#3f5a8c",       # 按钮边框
    "primary_button_bg": "#2f5e9e",   # 主按钮背景
    "primary_button_fg": "#ffffff",   # 主按钮字体
    "primary_button_hover_bg": "#3b6fb8", # 主按钮悬停
    "primary_button_active_bg": "#4a7fd0", # 主按钮激活背景
    "success_button_bg": "#2e7d32",   # 成功按钮背景
    "success_button_fg": "#ffffff",   # 成功按钮字体
    "success_button_hover_bg": "#388e3c", # 成功按钮悬停
    "success_button_active_bg": "#43a047", # 成功按钮激活背景
    "highlight": "#4d7bff",           # 高亮色
    "secondary_highlight": "#7ba6ff", # 次级高亮
    "theme_btn_text": "🌌",            # 主题按钮图标
    "theme_btn_hover_bg": "#2a3b5f",   # 主题按钮悬停
    "settings_btn_text": "⚙️",
    "settings_btn_hover_bg": "#2a3b5f", # 设置按钮悬停
    "header_bg": "#0f1625",            # 标题栏背景
    "header_fg": "#b0d4ff",            # 标题栏字体
    "header_border": "#1d2b48",        # 标题栏边框
    "frame_border": "#1d2b48",         # 框架边框
    "scrollbar_bg": "#2e3f5e",         # 滚动条滑块
    "scrollbar_trough": "#1a2538",     # 滚动条轨道
    "scrollbar_hover": "#4d7bff",      # 滚动条悬停
    "border": "#2e3f5e",               # 通用边框
}

# 暗夜星辰主题
DARK_STAR_THEME = {
    "bg": "#121212",                # 纯黑背景
    "secondary_bg": "#1e1e1e",      # 稍亮次级背景
    "fg": "#e0e0e0",                # 字体
    "accent_fg": "#bb86fc",          # 紫色强调
    "text_bg": "#212121",            # 文本框背景
    "text_fg": "#ffffff",            # 文本框字体
    "text_border": "#333333",        # 文本框边框
    "button_bg": "#2d2d2d",          # 按钮背景
    "button_fg": "#e0e0e0",          # 按钮字体
    "button_hover_bg": "#3a3a3a",    # 按钮悬停
    "button_active_bg": "#4a4a4a",   # 按钮激活
    "button_border": "#444444",      # 按钮边框
    "primary_button_bg": "#6200ee",  # 紫色按钮
    "primary_button_fg": "#ffffff",  # 主按钮字体
    "primary_button_hover_bg": "#7c4dff", # 主按钮悬停
    "primary_button_active_bg": "#9d6dff", # 主按钮激活背景
    "success_button_bg": "#03dac6",  # 青色按钮
    "success_button_fg": "#000000",  # 成功按钮字体
    "success_button_hover_bg": "#00e5c3", # 成功按钮悬停
    "success_button_active_bg": "#00f5d4", # 成功按钮激活背景
    "highlight": "#bb86fc",          # 紫色高亮
    "secondary_highlight": "#cf9fff", # 浅紫高亮
    "theme_btn_text": "🌃",           # 主题按钮图标
    "theme_btn_hover_bg": "#333333",  # 主题按钮悬停
    "settings_btn_text": "⚙️",
    "settings_btn_hover_bg": "#333333", # 设置按钮悬停
    "header_bg": "#0a0a0a",           # 标题栏背景
    "header_fg": "#e0e0e0",           # 标题栏字体
    "header_border": "#1a1a1a",       # 标题栏边框
    "frame_border": "#333333",        # 框架边框
    "scrollbar_bg": "#333333",        # 滚动条滑块
    "scrollbar_trough": "#1a1a1a",    # 滚动条轨道
    "scrollbar_hover": "#6200ee",     # 滚动条悬停
    "border": "#444444",              # 通用边框
}

# 科技绿主题
TECH_GREEN_THEME = {
    "bg": "#0a1f0a",                 # 深绿背景
    "secondary_bg": "#132813",        # 次级背景
    "fg": "#c8ffc8",                  # 浅绿字体
    "accent_fg": "#7dff7d",           # 亮绿强调
    "text_bg": "#1a2e1a",             # 文本框背景
    "text_fg": "#ffffff",             # 文本框字体
    "text_border": "#2a4a2a",         # 文本框边框
    "button_bg": "#1e3a1e",           # 按钮背景
    "button_fg": "#c8ffc8",           # 按钮字体
    "button_hover_bg": "#2a4a2a",     # 按钮悬停
    "button_active_bg": "#3a5a3a",    # 按钮激活
    "button_border": "#2a6a2a",       # 按钮边框
    "primary_button_bg": "#2a7d2a",   # 主按钮背景
    "primary_button_fg": "#ffffff",   # 主按钮字体
    "primary_button_hover_bg": "#3a8d3a", # 主按钮悬停
    "primary_button_active_bg": "#4a9d4a", # 主按钮激活背景
    "success_button_bg": "#4caf50",   # 成功按钮
    "success_button_fg": "#ffffff",   # 成功按钮字体
    "success_button_hover_bg": "#5cbf60", # 成功按钮悬停
    "success_button_active_bg": "#6ccf70", # 成功按钮激活背景
    "highlight": "#4caf50",           # 绿色高亮
    "secondary_highlight": "#8bc34a", # 浅绿高亮
    "theme_btn_text": "🌿",            # 主题按钮图标
    "theme_btn_hover_bg": "#2a4a2a",  # 主题按钮悬停
    "settings_btn_text": "⚙️",
    "settings_btn_hover_bg": "#2a4a2a", # 设置按钮悬停
    "header_bg": "#0a1a0a",           # 标题栏背景
    "header_fg": "#a8ffa8",           # 标题栏字体
    "header_border": "#1a2a1a",       # 标题栏边框
    "frame_border": "#2a4a2a",        # 框架边框
    "scrollbar_bg": "#2a4a2a",        # 滚动条滑块
    "scrollbar_trough": "#1a2e1a",    # 滚动条轨道
    "scrollbar_hover": "#4caf50",     # 滚动条悬停
    "border": "#2a6a2a",              # 通用边框
}

# 晨曦白主题（暖白+米黄+橙黄）
DAWN_WHITE_THEME = {
    "bg": "#fdf5e6",                  # 暖白背景
    "secondary_bg": "#fff2df",         # 浅米黄次级背景
    "fg": "#5d4e3d",                   # 深暖灰字体
    "accent_fg": "#ffb347",            # 橙黄强调色
    "text_bg": "#ffffff",              # 文本框背景
    "text_fg": "#5d4e3d",              # 文本框字体
    "text_border": "#d2b48c",          # 浅棕边框
    "button_bg": "#f0e0c0",            # 淡米黄按钮
    "button_fg": "#5d4e3d",            # 按钮字体
    "button_hover_bg": "#e6d0a0",      # 按钮悬停
    "button_active_bg": "#d2b48c",     # 按钮激活
    "button_border": "#c4a484",        # 按钮边框
    "primary_button_bg": "#ff8c42",    # 暖橙主按钮
    "primary_button_fg": "#ffffff",    # 主按钮字体
    "primary_button_hover_bg": "#ff9f5c", # 主按钮悬停
    "primary_button_active_bg": "#e67e22", # 主按钮激活
    "success_button_bg": "#8bc34a",    # 柔和绿成功按钮
    "success_button_fg": "#ffffff",    # 成功按钮字体
    "success_button_hover_bg": "#9ccc65", # 成功按钮悬停
    "success_button_active_bg": "#7cb342", # 成功按钮激活
    "highlight": "#ffb347",            # 高亮色
    "secondary_highlight": "#ffcc80",  # 次级高亮
    "theme_btn_text": "☀️",             # 主题按钮图标
    "theme_btn_hover_bg": "#e6d0a0",   # 主题按钮悬停
    "settings_btn_text": "⚙️",
    "settings_btn_hover_bg": "#e6d0a0", # 设置按钮悬停
    "header_bg": "#fff2df",            # 标题栏背景
    "header_fg": "#5d4e3d",            # 标题栏字体
    "header_border": "#d2b48c",        # 标题栏边框
    "frame_border": "#d2b48c",         # 框架边框
    "scrollbar_bg": "#d2b48c",         # 滚动条滑块
    "scrollbar_trough": "#f0e0c0",     # 滚动条轨道
    "scrollbar_hover": "#ff8c42",      # 滚动条悬停
    "border": "#c4a484",               # 通用边框
}

# 极简灰主题（淡蓝+灰+白）
MINIMAL_GRAY_THEME = {
    "bg": "#e6f0fa",                  # 淡蓝灰背景
    "secondary_bg": "#ffffff",         # 纯白次级背景
    "fg": "#2c3e50",                   # 深蓝灰字体
    "accent_fg": "#4aa3df",            # 天蓝强调色
    "text_bg": "#ffffff",              # 文本框背景
    "text_fg": "#2c3e50",              # 文本框字体
    "text_border": "#b0bec5",          # 中灰边框
    "button_bg": "#e0e5ec",            # 浅灰按钮
    "button_fg": "#2c3e50",            # 按钮字体
    "button_hover_bg": "#d0d9e8",      # 按钮悬停
    "button_active_bg": "#c0c9d8",     # 按钮激活
    "button_border": "#90a4ae",        # 按钮边框
    "primary_button_bg": "#4aa3df",    # 天蓝主按钮
    "primary_button_fg": "#ffffff",    # 主按钮字体
    "primary_button_hover_bg": "#5eb6f0", # 主按钮悬停
    "primary_button_active_bg": "#3b8fc2", # 主按钮激活背景
    "success_button_bg": "#66bb6a",    # 薄荷绿成功按钮
    "success_button_fg": "#ffffff",    # 成功按钮字体
    "success_button_hover_bg": "#7ecb7f", # 成功按钮悬停
    "success_button_active_bg": "#4caf50", # 成功按钮激活背景
    "highlight": "#4aa3df",            # 高亮色
    "secondary_highlight": "#7fc5f0",  # 次级高亮
    "theme_btn_text": "🌤️",           # 主题按钮图标
    "theme_btn_hover_bg": "#d0d9e8",   # 主题按钮悬停
    "settings_btn_text": "⚙️",
    "settings_btn_hover_bg": "#d0d9e8", # 设置按钮悬停
    "header_bg": "#ffffff",            # 标题栏背景
    "header_fg": "#2c3e50",            # 标题栏字体
    "header_border": "#b0bec5",        # 标题栏边框
    "frame_border": "#b0bec5",         # 框架边框
    "scrollbar_bg": "#b0bec5",         # 滚动条滑块
    "scrollbar_trough": "#e0e5ec",     # 滚动条轨道
    "scrollbar_hover": "#4aa3df",      # 滚动条悬停
    "border": "#90a4ae",               # 通用边框
}

# 所有主题字典映射
THEME_DICT = {
    "space_blue": SPACE_BLUE_THEME,
    "dark_star": DARK_STAR_THEME,
    "tech_green": TECH_GREEN_THEME,
    "dawn_white": DAWN_WHITE_THEME,
    "minimal_gray": MINIMAL_GRAY_THEME,
}

# 主题显示名称（用于下拉菜单）
THEME_DISPLAY_NAMES = {
    "space_blue": "🌌 太空蓝 (深色)",
    "dark_star": "🌃 暗夜星辰 (深色)",
    "tech_green": "🌿 科技绿 (深色)",
    "dawn_white": "☀️ 晨曦白 (浅色)",
    "minimal_gray": "🌤️ 极简灰 (浅色)",
}

# 根据设置确定当前主题
current_theme = settings.get("theme", "space_blue")
if current_theme in THEME_DICT:
    theme = THEME_DICT[current_theme].copy()
else:
    current_theme = "space_blue"
    theme = SPACE_BLUE_THEME.copy()

# ---------- 自定义滚动条类 ----------
class AccentScrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kwargs):
        ttk.Scrollbar.__init__(self, master, **kwargs)
        
    def set_theme(self, theme_colors):
        """设置滚动条主题颜色"""
        style = ttk.Style()
        style_name = f"AccentScrollbar_{id(self)}.TScrollbar"
        
        # 尝试创建样式，如果已存在则忽略
        try:
            style.element_create(f"{style_name}.trough", "from", "clam")
            style.element_create(f"{style_name}.thumb", "from", "clam")
        except:
            pass
        
        style.layout(style_name, [
            (f"{style_name}.trough", {
                'sticky': 'nswe',
                'children': [
                    (f"{style_name}.thumb", {
                        'unit': '1',
                        'sticky': 'nswe'
                    })
                ]
            })
        ])
        
        style.configure(style_name,
            background=theme_colors["scrollbar_bg"],
            troughcolor=theme_colors["scrollbar_trough"],
            bordercolor=theme_colors["border"],
            lightcolor=theme_colors["border"],
            darkcolor=theme_colors["border"],
            arrowcolor=theme_colors["fg"],
            relief="flat"
        )
        
        style.map(style_name,
            background=[('active', theme_colors["scrollbar_hover"])]
        )
        
        self.configure(style=style_name)

# ---------- 自定义文本框类（只保留垂直滚动条，始终自动换行）----------
class TextWithScrollbars(tk.Frame):
    def __init__(self, master=None, **kwargs):
        """
        始终自动换行，只有垂直滚动条
        """
        tk.Frame.__init__(self, master)
        
        # 提取文本框专用参数
        text_kwargs = {}
        for key in ['font', 'undo', 'maxundo', 'relief', 'borderwidth', 'padx', 'pady',
                   'bg', 'fg', 'insertbackground', 'selectbackground', 'selectforeground',
                   'highlightbackground', 'highlightcolor', 'highlightthickness']:
            if key in kwargs:
                text_kwargs[key] = kwargs.pop(key)
        
        # 将剩余参数传递给Frame
        self.configure(**kwargs)
        
        # 如果没有指定字体，使用默认
        if 'font' not in text_kwargs:
            text_kwargs['font'] = ("Consolas", 11)
        
        # 创建文本框，固定自动换行
        self.text = tk.Text(
            self,
            wrap="word",
            **text_kwargs
        )
        
        # 创建垂直滚动条
        self.v_scrollbar = AccentScrollbar(self, orient=tk.VERTICAL)
        
        # 配置滚动条
        self.text.configure(yscrollcommand=self.v_scrollbar.set)
        self.v_scrollbar.configure(command=self.text.yview)
        
        # 使用grid布局
        self.text.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置网格权重
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 绑定鼠标滚轮事件
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Button-4>", self._on_mousewheel)
        self.text.bind("<Button-5>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        if event.num == 4 or event.delta > 0:
            self.text.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.text.yview_scroll(1, "units")
        return "break"
    
    def update_theme(self, theme_colors):
        """更新主题"""
        # 更新文本框
        self.text.configure(
            bg=theme_colors["text_bg"],
            fg=theme_colors["text_fg"],
            insertbackground=theme_colors["text_fg"],
            selectbackground=theme_colors["secondary_highlight"],
            selectforeground=theme_colors["text_fg"],
            highlightbackground=theme_colors["text_border"],
            highlightcolor=theme_colors["highlight"]
        )
        
        # 更新滚动条
        self.v_scrollbar.set_theme(theme_colors)
    
    # 以下方法代理给内部文本框，以保持兼容性
    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)
    
    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)
    
    def bind(self, *args, **kwargs):
        return self.text.bind(*args, **kwargs)

# ---------- 自定义按钮类（带悬停效果）----------
class HoverButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        # 提取自定义参数
        self.hover_bg = kwargs.pop('hover_bg', None)
        self.hover_fg = kwargs.pop('hover_fg', None)
        self.default_bg = kwargs.get('bg', None)
        self.default_fg = kwargs.get('fg', None)
        
        tk.Button.__init__(self, master, **kwargs)
        
        # 绑定鼠标事件
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # 存储原始背景和前景色
        if self.default_bg is None:
            self.default_bg = self.cget("bg")
        if self.default_fg is None:
            self.default_fg = self.cget("fg")
        
        # 如果没有指定悬停颜色，则使用默认颜色
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
        """更新悬停颜色"""
        if hover_bg is not None:
            self.hover_bg = hover_bg
        if hover_fg is not None:
            self.hover_fg = hover_fg

# ---------- 核心格式化函数（优化版）----------
def format_stellaris_script(text: str) -> str:
    """紧凑 → 可读"""
    # 使用预编译正则和更快的空白压缩
    text = RE_GE.sub('>=', text)
    text = RE_LE.sub('<=', text)
    text = ' '.join(text.split())  # 替代 strip() + re.sub(r'\s+', ' ', ...)
    text = RE_BRACES.sub(r' \1 ', text)
    text = RE_EQUAL.sub(r' = ', text)
    text = RE_LT.sub(r' < ', text)
    text = RE_GT.sub(r' > ', text)
    text = ' '.join(text.split())  # 再次压缩多余空格
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
    output = re.sub(r'\n{3,}', '\n\n', output)  # 这里仍保留正则，但影响不大
    output = output.rstrip() + '\n'
    return output

def remove_comments_and_format_block(block_lines: list[str]) -> str:
    """处理单个顶级块，去注释、压缩（优化版）"""
    processed_lines = []
    str_counter = 0
    str_map = {}

    for line in block_lines:
        # 使用字符串 split 替代正则分割（更快）
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

    result = ' '.join(processed_lines)  # 合并为一行

    # 收集标识符（使用预编译正则）
    identifiers = set(RE_IDENTIFIER.findall(result))
    underscore_protected = {}
    for i, word in enumerate(identifiers):
        if '_' in word and word not in str_map.values():
            placeholder = f"__ID_{i}__"
            underscore_protected[placeholder] = word
            result = result.replace(word, placeholder)  # 保持原逻辑

    # 压缩空白（使用 ' '.join(result.split()) 替代 re.sub）
    result = ' '.join(result.split())
    result = RE_OPERATOR_SPACE.sub(r' \1 ', result)
    result = RE_BRACKET_SPACE.sub(r'\1 ', result)
    result = ' '.join(result.split())  # 再次压缩

    for ph, original in underscore_protected.items():
        result = result.replace(ph, original)
    for ph, original in str_map.items():
        result = result.replace(ph, original)

    return result.strip()

def compact_stellaris_script(text: str) -> str:
    """原始脚本 → 紧凑"""
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

# ---------- 输出处理函数 ----------
def handle_output(result_text: str, operation_name: str):
    """根据输出模式处理结果"""
    if settings["output_mode"] and settings["output_file_path"]:
        # 输出到文件
        try:
            # 确保目录存在
            out_dir = os.path.dirname(settings["output_file_path"])
            if out_dir and not os.path.exists(out_dir):
                os.makedirs(out_dir, exist_ok=True)
            with open(settings["output_file_path"], 'w', encoding='utf-8') as f:
                f.write(result_text)
            # 在输出栏显示成功信息
            output_textbox.delete("1.0", tk.END)
            output_textbox.insert(tk.END, f"✓ {operation_name} 结果已保存至文件：\n{settings['output_file_path']}")
            # 添加成功样式（需要定义tag）
            output_textbox.text.tag_config("success", foreground="#4CAF50", font=("Consolas", 11, "bold"))
            output_textbox.text.tag_add("success", "1.0", "1.1")
        except Exception as e:
            output_textbox.delete("1.0", tk.END)
            output_textbox.insert(tk.END, f"❌ 写入文件失败：{e}\n\n结果将显示在此：\n{result_text}")
            output_textbox.text.tag_config("error", foreground="#f44336", font=("Consolas", 11, "bold"))
            output_textbox.text.tag_add("error", "1.0", "1.1")
    else:
        # 输出到界面
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, result_text)

def to_compact():
    input_text = input_textbox.get("1.0", tk.END).strip()
    if not input_text:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
        return
    try:
        result = compact_stellaris_script(input_text)
        handle_output(result, "转化为指令")
    except Exception as e:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, f"转换出错：{e}")
        output_textbox.text.tag_add("error", "1.0", "1.1")

def to_formatted():
    input_text = input_textbox.get("1.0", tk.END).strip()
    if not input_text:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
        return
    try:
        result = format_stellaris_script(input_text)
        handle_output(result, "指令格式化")
    except Exception as e:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, f"格式化出错：{e}")
        output_textbox.text.tag_add("error", "1.0", "1.1")

# ---------- 主题切换（随机） ----------
def toggle_theme():
    global current_theme, theme
    # 可用的主题键列表
    themes = list(THEME_DICT.keys())
    # 随机选择一个
    new_theme = random.choice(themes)
    current_theme = new_theme
    # 更新全局theme变量
    theme.clear()
    theme.update(THEME_DICT[current_theme])
    
    # 保存主题设置
    settings["theme"] = current_theme
    save_settings()
    
    # 应用新主题
    apply_theme()

def apply_theme():
    """应用当前主题到所有界面元素"""
    root.configure(bg=theme["bg"])
    
    # 更新标题栏
    header_frame.configure(bg=theme["header_bg"], highlightbackground=theme["header_border"], highlightthickness=1)
    title_label.configure(bg=theme["header_bg"], fg=theme["header_fg"])
    label_input.configure(bg=theme["header_bg"], fg=theme["header_fg"])
    
    # 更新主题按钮
    theme_btn.configure(
        text=theme["theme_btn_text"],
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    theme_btn.default_bg = theme["button_bg"]
    theme_btn.default_fg = theme["button_fg"]
    theme_btn.update_hover_colors(hover_bg=theme["theme_btn_hover_bg"])
    
    # 更新设置按钮
    settings_btn.configure(
        text=theme["settings_btn_text"],
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    settings_btn.default_bg = theme["button_bg"]
    settings_btn.default_fg = theme["button_fg"]
    settings_btn.update_hover_colors(hover_bg=theme["settings_btn_hover_bg"])
    
    # 更新输出模式按钮
    update_output_mode_button()
    
    # 更新输入框框架
    input_frame.configure(bg=theme["secondary_bg"], highlightbackground=theme["frame_border"], highlightthickness=1)
    input_textbox.update_theme(theme)
    
    # 更新按钮框架
    btn_frame.configure(bg=theme["secondary_bg"], highlightbackground=theme["frame_border"], highlightthickness=1)
    
    # 更新主按钮
    btn_to_formatted.configure(
        bg=theme["primary_button_bg"],
        fg=theme["primary_button_fg"],
        activebackground=theme["primary_button_active_bg"]
    )
    btn_to_formatted.default_bg = theme["primary_button_bg"]
    btn_to_formatted.default_fg = theme["primary_button_fg"]
    btn_to_formatted.update_hover_colors(hover_bg=theme["primary_button_hover_bg"])
    
    btn_to_compact.configure(
        bg=theme["primary_button_bg"],
        fg=theme["primary_button_fg"],
        activebackground=theme["primary_button_active_bg"]
    )
    btn_to_compact.default_bg = theme["primary_button_bg"]
    btn_to_compact.default_fg = theme["primary_button_fg"]
    btn_to_compact.update_hover_colors(hover_bg=theme["primary_button_hover_bg"])
    
    # 更新输出框框架
    output_frame.configure(bg=theme["secondary_bg"], highlightbackground=theme["frame_border"], highlightthickness=1)
    label_output.configure(bg=theme["secondary_bg"], fg=theme["accent_fg"])
    output_textbox.update_theme(theme)
    
    # 更新版本标签
    version_label.configure(bg=theme["bg"], fg=theme["fg"])

# ---------- 输出模式切换 ----------
def toggle_output_mode():
    settings["output_mode"] = not settings["output_mode"]
    update_output_mode_button()
    save_settings()

def update_output_mode_button():
    if settings["output_mode"]:
        output_mode_btn.configure(
            text="📁 文件输出",
            bg=theme["success_button_bg"],
            fg=theme["success_button_fg"],
            activebackground=theme["success_button_active_bg"]
        )
        output_mode_btn.default_bg = theme["success_button_bg"]
        output_mode_btn.default_fg = theme["success_button_fg"]
        output_mode_btn.update_hover_colors(hover_bg=theme["success_button_hover_bg"])
    else:
        output_mode_btn.configure(
            text="📄 界面输出",
            bg=theme["button_bg"],
            fg=theme["button_fg"],
            activebackground=theme["button_active_bg"]
        )
        output_mode_btn.default_bg = theme["button_bg"]
        output_mode_btn.default_fg = theme["button_fg"]
        output_mode_btn.update_hover_colors(hover_bg=theme["button_hover_bg"])

# ---------- 设置窗口（已移除换行模式选择，更新检查更新和关于）----------
def open_settings():
    """打开设置窗口"""
    settings_win = Toplevel(root)
    settings_win.title("设置")
    settings_win.resizable(False, False)
    settings_win.configure(bg=theme["secondary_bg"])
    settings_win.transient(root)
    settings_win.grab_set()
    
    # 窗口尺寸
    win_width = 550
    win_height = 480
    settings_win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (win_width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (win_height // 2)
    settings_win.geometry(f"{win_width}x{win_height}+{x}+{y}")
    
    # 标题
    title_frame = tk.Frame(settings_win, bg=theme["header_bg"], height=40)
    title_frame.pack(fill="x", pady=(0, 10))
    title_frame.pack_propagate(False)
    
    tk.Label(
        title_frame,
        text="Stellaris 脚本转换工具 - 设置",
        bg=theme["header_bg"],
        fg=theme["header_fg"],
        font=("微软雅黑", 12, "bold")
    ).pack(expand=True)
    
    # 版本信息
    version_frame = tk.Frame(settings_win, bg=theme["secondary_bg"])
    version_frame.pack(fill="x", pady=(5, 10), padx=20)
    
    tk.Label(
        version_frame,
        text="当前版本：1.3",
        bg=theme["secondary_bg"],
        fg=theme["fg"],
        font=("微软雅黑", 10)
    ).pack(side="left")
    
    # 主题选择
    theme_frame = tk.Frame(settings_win, bg=theme["secondary_bg"])
    theme_frame.pack(pady=5, padx=20, fill="x")
    
    tk.Label(
        theme_frame,
        text="主题选择：",
        bg=theme["secondary_bg"],
        fg=theme["fg"],
        font=("微软雅黑", 9)
    ).pack(anchor="w")
    
    theme_select_frame = tk.Frame(theme_frame, bg=theme["secondary_bg"])
    theme_select_frame.pack(fill="x", pady=5)
    
    # 主题下拉菜单
    theme_var = tk.StringVar(value=THEME_DISPLAY_NAMES[current_theme])
    
    def on_theme_change(*args):
        global current_theme, theme
        selected_display = theme_var.get()
        # 根据显示名称找到对应的主题键
        selected_key = None
        for key, display in THEME_DISPLAY_NAMES.items():
            if display == selected_display:
                selected_key = key
                break
        if selected_key and selected_key != current_theme:
            current_theme = selected_key
            theme.clear()
            theme.update(THEME_DICT[current_theme])
            settings["theme"] = current_theme
            save_settings()
            apply_theme()
    
    theme_menu = tk.OptionMenu(
        theme_select_frame,
        theme_var,
        *THEME_DISPLAY_NAMES.values(),
        command=lambda _: on_theme_change()
    )
    theme_menu.config(
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        activeforeground=theme["button_fg"],
        font=("微软雅黑", 9),
        bd=2,
        relief="raised"
    )
    theme_menu.pack(side="left", fill="x", expand=True)
    
    # 文件路径设置框架
    path_frame = tk.Frame(settings_win, bg=theme["secondary_bg"])
    path_frame.pack(pady=10, padx=20, fill="x")
    
    tk.Label(
        path_frame,
        text="输出文件路径：",
        bg=theme["secondary_bg"],
        fg=theme["fg"],
        font=("微软雅黑", 9)
    ).pack(anchor="w")
    
    # 路径输入框和按钮框架
    path_input_frame = tk.Frame(path_frame, bg=theme["secondary_bg"])
    path_input_frame.pack(fill="x", pady=5)
    
    # 临时变量
    temp_path_var = tk.StringVar(value=settings["output_file_path"])
    
    # 路径输入框
    path_entry = tk.Entry(
        path_input_frame,
        textvariable=temp_path_var,
        bg=theme["text_bg"],
        fg=theme["text_fg"],
        insertbackground=theme["text_fg"],
        font=("Consolas", 9),
        bd=2,
        relief="sunken",
        highlightbackground=theme["text_border"],
        highlightcolor=theme["highlight"],
        highlightthickness=1
    )
    path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    # 浏览按钮
    def browse_file():
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            temp_path_var.set(file_path)
            settings["output_file_path"] = file_path
            save_settings()
    
    browse_btn = HoverButton(
        path_input_frame,
        text="浏览",
        command=browse_file,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        hover_bg=theme["button_hover_bg"],
        font=("微软雅黑", 9),
        relief="raised",
        bd=2,
        padx=15,
        pady=3
    )
    browse_btn.pack(side="left", padx=(0, 5))
    
    # 保存按钮
    def save_settings_and_close():
        settings["output_file_path"] = temp_path_var.get()
        save_settings()
        settings_win.destroy()
    
    save_btn = HoverButton(
        path_input_frame,
        text="保存设置",
        command=save_settings_and_close,
        bg=theme["primary_button_bg"],
        fg=theme["primary_button_fg"],
        activebackground=theme["primary_button_active_bg"],
        hover_bg=theme["primary_button_hover_bg"],
        font=("微软雅黑", 9, "bold"),
        relief="raised",
        bd=2,
        padx=15,
        pady=3
    )
    save_btn.pack(side="left")
    
    # 分隔线
    separator = tk.Frame(settings_win, bg=theme["border"], height=2)
    separator.pack(fill=tk.X, padx=20, pady=15)
    
    # 垂直按钮框架（放置检查更新、关于、关闭）
    vertical_btn_frame = tk.Frame(settings_win, bg=theme["secondary_bg"])
    vertical_btn_frame.pack(pady=20, padx=20, fill="x")
    
    # ----- 修改检查更新功能 -----
    def check_update():
        # 打开项目主页
        webbrowser.open("https://github.com/Birdlaiwatin/Stellaris-Script-Formatter")
        messagebox.showinfo("检查更新", "已为您打开项目主页，请查看最新版本。")
    
    check_btn = HoverButton(
        vertical_btn_frame,
        text="检查更新",
        command=check_update,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        hover_bg=theme["button_hover_bg"],
        font=("微软雅黑", 10),
        relief="raised",
        bd=2,
        width=20,
        padx=10,
        pady=5
    )
    check_btn.pack(pady=3)
    
    # ----- 修改关于窗口 -----
    def show_about():
        about_win = Toplevel(settings_win)
        about_win.title("关于")
        about_win.resizable(False, False)
        about_win.configure(bg=theme["secondary_bg"])
        about_win.transient(settings_win)
        about_win.grab_set()
        
        # 增大窗口以容纳项目地址
        about_win.update_idletasks()
        x = settings_win.winfo_x() + (settings_win.winfo_width() // 2) - 200
        y = settings_win.winfo_y() + (settings_win.winfo_height() // 2) - 150
        about_win.geometry(f"400x250+{x}+{y}")
        
        tk.Label(
            about_win,
            text="Stellaris 脚本转换工具\n\n"
                 "版本 1.3\n\n"
                 "专为《群星》脚本转换格式设计\n\n",
                 #"项目主页：https://github.com/Birdlaiwatin/Stellaris-Script-Formatter",
            bg=theme["secondary_bg"],
            fg=theme["fg"],
            font=("微软雅黑", 10),
            justify="center"
        ).pack(expand=True, pady=20)
        
        close_about_btn = HoverButton(
            about_win,
            text="关闭",
            command=about_win.destroy,
            bg=theme["primary_button_bg"],
            fg=theme["primary_button_fg"],
            activebackground=theme["primary_button_active_bg"],
            hover_bg=theme["primary_button_hover_bg"],
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
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        hover_bg=theme["button_hover_bg"],
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
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        hover_bg=theme["button_hover_bg"],
        font=("微软雅黑", 10),
        relief="raised",
        bd=2,
        width=20,
        padx=10,
        pady=5
    )
    close_btn.pack(pady=3)

# ---------- 创建主窗口 ----------
root = tk.Tk()
root.title("Stellaris 脚本转换工具 v1.3")
root.geometry("900x750")
root.configure(bg=theme["bg"])
root.minsize(800, 600)

# ---------- 标题栏 ----------
header_frame = tk.Frame(
    root,
    bg=theme["header_bg"],
    highlightbackground=theme["header_border"],
    highlightthickness=1
)
header_frame.pack(fill="x", padx=10, pady=(10, 0))

# 标题
title_label = tk.Label(
    header_frame,
    text="Stellaris 脚本转换工具",
    anchor="w",
    bg=theme["header_bg"],
    fg=theme["header_fg"],
    font=("微软雅黑", 12, "bold")
)
title_label.pack(side="left", padx=15, pady=10)

# 输入标签
label_input = tk.Label(
    header_frame,
    text="输入原始脚本：",
    anchor="w",
    bg=theme["header_bg"],
    fg=theme["header_fg"],
    font=("微软雅黑", 10)
)
label_input.pack(side="left", padx=(20, 0))

# 主题切换按钮
theme_btn = HoverButton(
    header_frame,
    text=theme["theme_btn_text"],
    command=toggle_theme,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    hover_bg=theme["theme_btn_hover_bg"],
    font=("Segoe UI", 12),
    width=3,
    bd=2,
    relief="raised"
)
theme_btn.pack(side="right", padx=5, pady=5)

# 设置按钮
settings_btn = HoverButton(
    header_frame,
    text=theme["settings_btn_text"],
    command=open_settings,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    hover_bg=theme["settings_btn_hover_bg"],
    font=("Segoe UI", 12),
    width=3,
    bd=2,
    relief="raised"
)
settings_btn.pack(side="right", padx=5, pady=5)

# 输出模式按钮
output_mode_btn = HoverButton(
    header_frame,
    text="",  # 稍后设置
    command=toggle_output_mode,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    hover_bg=theme["button_hover_bg"],
    font=("微软雅黑", 9),
    bd=2,
    relief="raised",
    padx=10
)
output_mode_btn.pack(side="right", padx=(0, 5), pady=5)
update_output_mode_button()

# ---------- 输入框框架（固定高度200）----------
input_frame = tk.Frame(
    root,
    bg=theme["secondary_bg"],
    highlightbackground=theme["frame_border"],
    highlightthickness=1,
    height=200
)
input_frame.pack(fill="x", padx=10, pady=5)
input_frame.pack_propagate(False)  # 禁止框架调整大小

# 输入文本框（使用自定义类）
input_textbox = TextWithScrollbars(
    input_frame,
    font=("Consolas", 11)
)
input_textbox.pack(fill="both", expand=True, padx=5, pady=5)

# ---------- 按钮框架 ----------
btn_frame = tk.Frame(
    root,
    bg=theme["secondary_bg"],
    highlightbackground=theme["frame_border"],
    highlightthickness=1
)
btn_frame.pack(pady=10, padx=10, fill="x")

# 格式化按钮
btn_to_formatted = HoverButton(
    btn_frame,
    text="指令格式化 ⬅",
    command=to_formatted,
    bg=theme["primary_button_bg"],
    fg=theme["primary_button_fg"],
    activebackground=theme["primary_button_active_bg"],
    hover_bg=theme["primary_button_hover_bg"],
    font=("微软雅黑", 10, "bold"),
    height=1,
    bd=3,
    relief="raised",
    padx=20,
    pady=8
)
btn_to_formatted.pack(side="left", expand=True, fill="x", padx=20, pady=10)

# 转化为指令按钮
btn_to_compact = HoverButton(
    btn_frame,
    text="➡ 转化为指令",
    command=to_compact,
    bg=theme["primary_button_bg"],
    fg=theme["primary_button_fg"],
    activebackground=theme["primary_button_active_bg"],
    hover_bg=theme["primary_button_hover_bg"],
    font=("微软雅黑", 10, "bold"),
    height=1,
    bd=3,
    relief="raised",
    padx=20,
    pady=8
)
btn_to_compact.pack(side="left", expand=True, fill="x", padx=20, pady=10)

# ---------- 输出框框架（自适应剩余空间）----------
output_frame = tk.Frame(
    root,
    bg=theme["secondary_bg"],
    highlightbackground=theme["frame_border"],
    highlightthickness=1
)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

# 输出标签
label_output = tk.Label(
    output_frame,
    text="转换结果：",
    anchor="w",
    bg=theme["secondary_bg"],
    fg=theme["accent_fg"],
    font=("微软雅黑", 10, "bold")
)
label_output.pack(fill="x", padx=10, pady=(5, 0))

# 输出文本框（使用自定义类）
output_textbox = TextWithScrollbars(
    output_frame,
    font=("Consolas", 11)
)
output_textbox.pack(fill="both", expand=True, padx=5, pady=5)

# 版本信息标签
version_label = tk.Label(
    root,
    text="v1.3 | 专为《群星》脚本转换格式设计",
    anchor="center",
    bg=theme["bg"],
    fg=theme["fg"],
    font=("微软雅黑", 8)
)
version_label.pack(fill="x", pady=(5, 10))

# 应用初始主题
apply_theme()

# 启动主循环
root.mainloop()