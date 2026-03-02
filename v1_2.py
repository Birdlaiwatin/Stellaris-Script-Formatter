import re
import json
import os
import sys
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, Toplevel
from typing import List

# ---------- 获取程序所在目录（兼容脚本和exe）----------
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
SETTINGS_FILE = os.path.join(BASE_DIR, 'settings.json')

# ---------- 默认设置 ----------
DEFAULT_SETTINGS = {
    "output_mode": False,          # False=输出到界面，True=输出到文件
    "output_file_path": "",         # 默认空，需要用户设置
    "theme": "dark"                 # 默认深色主题
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

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存设置出错: {e}")

# 初始加载
load_settings()

# ---------- 主题配色 ----------
DARK_THEME = {
    "bg": "#2b2b2b",
    "fg": "#f0f0f0",
    "text_bg": "#3c3f41",
    "text_fg": "#ffffff",
    "button_bg": "#4e5254",
    "button_fg": "#ffffff",
    "button_active_bg": "#5e6264",
    "button_highlight": "#6a6e70",
    "button_shadow": "#2a2e30",
    "highlight": "#4a6c8f",
    "theme_btn_text": "☀️",         # 深色模式显示太阳，点击切换到浅色
    #"theme_btn_bg": "#fea743",
    "theme_btn_relief": "raised",
    "settings_btn_text": "⚙️",
}

LIGHT_THEME = {
    "bg": "#f0f0f0",
    "fg": "#000000",
    "text_bg": "#ffffff",
    "text_fg": "#000000",
    "button_bg": "#e1e1e1",
    "button_fg": "#000000",
    "button_active_bg": "#d0d0d0",
    "button_highlight": "#f0f0f0",
    "button_shadow": "#a0a0a0",
    "highlight": "#0078d7",
    "theme_btn_text": "🌙",         # 浅色模式显示月亮，点击切换到深色
    #"theme_btn_bg": "#00aeff",
    "theme_btn_relief": "raised",
    "settings_btn_text": "⚙️",
}

# 根据设置确定当前主题
current_theme = settings.get("theme", "dark")
if current_theme == "dark":
    theme = DARK_THEME.copy()
else:
    theme = LIGHT_THEME.copy()

# ---------- 核心格式化函数（保持不变） ----------
def format_stellaris_script(text: str) -> str:
    """紧凑 → 可读"""
    text = re.sub(r'>\s*=', '>=', text)
    text = re.sub(r'<\s*=', '<=', text)
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'([{}])', r' \1 ', text)
    text = re.sub(r'(?<![<>])=(?!=)', r' = ', text)
    text = re.sub(r'(?<!<)(?<!>)(?<!=)<(?!=)', r' < ', text)
    text = re.sub(r'(?<!<)(?<!>)(?<!=)>(?!=)', r' > ', text)
    text = re.sub(r'\s+', ' ', text).strip()

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
    output = output.rstrip() + '\n'
    return output

def remove_comments_and_format_block(block_lines: list[str]) -> str:
    """处理单个顶级块，去注释、压缩"""
    processed_lines = []
    str_counter = 0
    str_map = {}

    for line in block_lines:
        line = re.split(r'\s*#', line, 1)[0].rstrip()
        if not line.strip():
            continue

        def protect_str(match):
            nonlocal str_counter
            placeholder = f"__STR_{str_counter}__"
            str_map[placeholder] = match.group(0)
            str_counter += 1
            return placeholder

        line = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', protect_str, line)
        line = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", protect_str, line)
        processed_lines.append(line)

    if not processed_lines:
        return ""

    result = ' '.join(processed_lines)

    identifiers = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', result))
    underscore_protected = {}
    for i, word in enumerate(identifiers):
        if '_' in word and word not in str_map.values():
            placeholder = f"__ID_{i}__"
            underscore_protected[placeholder] = word
            result = result.replace(word, placeholder)

    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*([=<>!]=?|\+=|-=|\*=|/=|==|!=|>=|<=|>|<)\s*', r' \1 ', result)
    result = re.sub(r'\s*([{}[\](),;])\s*', r'\1 ', result)
    result = re.sub(r'\s+', ' ', result)

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
        except Exception as e:
            output_textbox.delete("1.0", tk.END)
            output_textbox.insert(tk.END, f"❌ 写入文件失败：{e}\n\n结果将显示在此：\n{result_text}")
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

# ---------- 主题切换 ----------
def toggle_theme():
    global current_theme, theme
    if current_theme == "dark":
        current_theme = "light"
        theme = LIGHT_THEME
    else:
        current_theme = "dark"
        theme = DARK_THEME

    # 保存主题设置
    settings["theme"] = current_theme
    save_settings()

    # 更新主窗口
    root.configure(bg=theme["bg"])
    header_frame.configure(bg=theme["bg"])
    label_input.configure(bg=theme["bg"], fg=theme["fg"])

    # 更新输出模式按钮
    output_mode_btn.configure(
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    # 输出模式按钮颜色可能已由 ON/OFF 改变，重新应用正确颜色
    update_output_mode_button()

    # 更新主题按钮
    theme_btn.configure(
        text=theme["theme_btn_text"],
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    # 更新设置按钮
    settings_btn.configure(
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    # 更新输入框
    input_textbox.configure(
        bg=theme["text_bg"],
        fg=theme["text_fg"],
        insertbackground=theme["text_fg"],
        highlightbackground=theme["highlight"],
        highlightcolor=theme["highlight"]
    )
    # 更新按钮框架
    btn_frame.configure(bg=theme["bg"])
    # 更新两个主按钮
    btn_to_compact.configure(
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    btn_to_formatted.configure(
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"]
    )
    # 更新输出标签
    label_output.configure(bg=theme["bg"], fg=theme["fg"])
    # 更新输出框
    output_textbox.configure(
        bg=theme["text_bg"],
        fg=theme["text_fg"],
        insertbackground=theme["text_fg"],
        highlightbackground=theme["highlight"],
        highlightcolor=theme["highlight"]
    )

# ---------- 输出模式切换 ----------
def toggle_output_mode():
    settings["output_mode"] = not settings["output_mode"]
    update_output_mode_button()
    save_settings()

def update_output_mode_button():
    if settings["output_mode"]:
        #"📁文件输出 ON"
        output_mode_btn.config(text="📁文件输出 ", bg="#5a8c5a" if current_theme=="dark" else "#8fc98f")
    else:
        output_mode_btn.config(text="📄界面输出 ", bg=theme["button_bg"])

# ---------- 设置窗口 ----------
def open_settings():
    """打开设置窗口（居中、可调整大小、按钮按需排列）"""
    settings_win = Toplevel(root)
    settings_win.title("设置")
    settings_win.resizable(True, True)        # 允许调整大小
    settings_win.configure(bg=theme["bg"])
    settings_win.transient(root)
    settings_win.grab_set()

    # 计算居中位置并一次性设置窗口大小和位置（避免闪烁）
    win_width = 500
    win_height = 260                           # 适当增加高度以容纳纵排按钮
    settings_win.update_idletasks()             # 确保窗口信息更新
    x = root.winfo_x() + (root.winfo_width() // 2) - (win_width // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (win_height // 2)
    settings_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # 版本信息
    version_label = tk.Label(
        settings_win,
        text="当前版本：1.2",
        bg=theme["bg"],
        fg=theme["fg"],
        font=("微软雅黑", 11)
    )
    version_label.pack(pady=(10, 5))

    # 文件路径设置框架
    path_frame = tk.Frame(settings_win, bg=theme["bg"])
    path_frame.pack(pady=5, padx=20, fill="x")

    tk.Label(path_frame, text="输出文件路径：", bg=theme["bg"], fg=theme["fg"]).pack(anchor="w")

    path_entry_frame = tk.Frame(path_frame, bg=theme["bg"])
    path_entry_frame.pack(fill="x", pady=5)

    # 临时变量，用于存储用户输入（点击保存后才写入settings）
    temp_path_var = tk.StringVar(value=settings["output_file_path"])

    # 路径输入框
    path_entry = tk.Entry(
        path_entry_frame,
        textvariable=temp_path_var,
        bg=theme["text_bg"],
        fg=theme["text_fg"],
        insertbackground=theme["text_fg"],
        font=("Consolas", 9),
        bd=2,
        relief="sunken"
    )
    path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

    # 保存按钮（放在浏览按钮左边）
    def save_settings_and_close():
        settings["output_file_path"] = temp_path_var.get()
        save_settings()
        settings_win.destroy()

    save_btn = tk.Button(
        path_entry_frame,
        text="保存",
        command=save_settings_and_close,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        relief="raised",
        bd=3,
        padx=10
    )
    save_btn.pack(side="left", padx=(0, 5))

    # 浏览按钮（修改点：选择后立即写入设置）
    def browse_file():
        file_path = filedialog.asksaveasfilename(
            title="选择输出文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            temp_path_var.set(file_path)          # 更新输入框显示
            settings["output_file_path"] = file_path  # 立即写入全局设置
            save_settings()                        # 保存到配置文件

    browse_btn = tk.Button(
        path_entry_frame,
        text="浏览",
        command=browse_file,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        relief="raised",
        bd=3,
        padx=10
    )
    browse_btn.pack(side="left")

    # 垂直按钮框架（用于放置检查更新和关闭）
    vertical_btn_frame = tk.Frame(settings_win, bg=theme["bg"])
    vertical_btn_frame.pack(pady=10)

    def check_update():
        messagebox.showinfo("检查更新", "当前已是最新版本 (1.2)")

    check_btn = tk.Button(
        vertical_btn_frame,
        text="检查更新",
        command=check_update,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        font=("微软雅黑", 10),
        relief="raised",
        bd=3,
        width=12,
        padx=10,
        pady=5
    )
    check_btn.pack(pady=5)

    close_btn = tk.Button(
        vertical_btn_frame,
        text="关闭",
        command=settings_win.destroy,
        bg=theme["button_bg"],
        fg=theme["button_fg"],
        activebackground=theme["button_active_bg"],
        font=("微软雅黑", 10),
        relief="raised",
        bd=3,
        width=12,
        padx=10,
        pady=5
    )
    close_btn.pack(pady=5)

# ---------- 创建主窗口 ----------
root = tk.Tk()
root.title("Stellaris 脚本转换工具 v1.2")
root.geometry("900x700")
root.configure(bg=theme["bg"])

# ---------- 标题栏（输入标签 + 输出模式按钮 + 主题切换 + 设置）----------
header_frame = tk.Frame(root, bg=theme["bg"])
header_frame.pack(fill="x", padx=10, pady=(10, 0))

label_input = tk.Label(
    header_frame,
    text="输入原始脚本：",
    anchor="w",
    bg=theme["bg"],
    fg=theme["fg"],
    font=("微软雅黑", 10)
)
label_input.pack(side="left")

# 输出模式按钮（放在主题按钮和设置按钮之前）
output_mode_btn = tk.Button(
    header_frame,
    text="",  # 稍后设置
    command=toggle_output_mode,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    font=("微软雅黑", 10),
    bd=3,
    relief="raised",
    padx=10
)
output_mode_btn.pack(side="right", padx=(0,5))
update_output_mode_button()  # 初始化显示

# 设置按钮（⚙️）
settings_btn = tk.Button(
    header_frame,
    text=theme["settings_btn_text"],
    command=open_settings,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    font=("Segoe UI", 12),
    width=3,
    bd=3,
    relief="raised"
)
settings_btn.pack(side="right", padx=(0,5))

# 主题切换按钮
theme_btn = tk.Button(
    header_frame,
    text=theme["theme_btn_text"],
    command=toggle_theme,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    font=("Segoe UI", 12),
    width=3,
    bd=3,
    relief="raised"
)
theme_btn.pack(side="right")

# ---------- 输入文本框 ----------
input_textbox = scrolledtext.ScrolledText(
    root,
    height=12,
    font=("Consolas", 11),
    bg=theme["text_bg"],
    fg=theme["text_fg"],
    insertbackground=theme["text_fg"],
    highlightbackground=theme["highlight"],
    highlightcolor=theme["highlight"],
    relief="sunken",
    bd=2
)
input_textbox.pack(fill="both", expand=True, padx=10, pady=5)

# ---------- 按钮框架 ----------
btn_frame = tk.Frame(root, bg=theme["bg"])
btn_frame.pack(pady=10)

btn_to_formatted = tk.Button(
    btn_frame,
    text="指令格式化 ⬅",
    command=to_formatted,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    font=("微软雅黑", 10),
    width=15,
    height=1,
    bd=3,
    relief="raised",
    padx=10,
    pady=5
)
btn_to_formatted.pack(side="left", padx=10)

btn_to_compact = tk.Button(
    btn_frame,
    text="➡ 转化为指令",
    command=to_compact,
    bg=theme["button_bg"],
    fg=theme["button_fg"],
    activebackground=theme["button_active_bg"],
    font=("微软雅黑", 10),
    width=15,
    height=1,
    bd=3,
    relief="raised",
    padx=10,
    pady=5
)
btn_to_compact.pack(side="left", padx=10)


# ---------- 输出标签 ----------
label_output = tk.Label(
    root,
    text="转换结果：",
    anchor="w",
    bg=theme["bg"],
    fg=theme["fg"],
    font=("微软雅黑", 10)
)
label_output.pack(fill="x", padx=10, pady=(5, 0))

# ---------- 输出文本框 ----------
output_textbox = scrolledtext.ScrolledText(
    root,
    height=12,
    font=("Consolas", 11),
    bg=theme["text_bg"],
    fg=theme["text_fg"],
    insertbackground=theme["text_fg"],
    highlightbackground=theme["highlight"],
    highlightcolor=theme["highlight"],
    relief="sunken",
    bd=2
)
output_textbox.pack(fill="both", expand=True, padx=10, pady=5)

# 启动主循环
root.mainloop()