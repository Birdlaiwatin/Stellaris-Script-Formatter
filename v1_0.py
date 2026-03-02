import re
import tkinter as tk
from tkinter import scrolledtext
from typing import List

# ---------- 第一个脚本：压缩功能（原去除注释、合并为单行） ----------
def remove_comments_and_format_block(block_lines: list[str]) -> str:
    """处理单个顶级块，去注释、压缩、规范空格"""
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
    """压缩脚本：去除注释，合并顶级块为单行，用换行分隔块"""
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


# ---------- 第二个脚本：美化功能（还原为可读格式） ----------
def pretty_format_stellaris_script(text: str) -> str:
    """
    把群星紧凑格式的effect/event/script格式化成可读形式
    特点：
    - { 紧跟 = 后面（仅一个空格）
    - 每个键值对后换行
    - } 与对应层对齐
    - 正确处理 >=、<=、<、> 等运算符
    """
    # 先保护比较运算符，避免被空格分隔
    text = re.sub(r'>\s*=', '>=', text)
    text = re.sub(r'<\s*=', '<=', text)
    
    # 统一空白为单个空格
    text = re.sub(r'\s+', ' ', text.strip())

    # 在关键符号前后加空格（但不处理 >= 和 <= 内部）
    text = re.sub(r'([{}])', r' \1 ', text)
    text = re.sub(r'(?<![<>])=(?!=)', r' = ', text)  # = 前后加空格，但不破坏 >= <=
    text = re.sub(r'(?<!<)(?<!>)(?<!=)<(?!=)', r' < ', text)  # 独立的 <
    text = re.sub(r'(?<!<)(?<!>)(?<!=)>(?!=)', r' > ', text)  # 独立的 >
    
    # 清理多余空格
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
            # { 紧跟上一行末尾，确保只有一个空格
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

            # 连续 } 之间适当加空行
            if last_was_closing_brace and indent > 0:
                remaining = ' '.join(tokens[i+1:]).strip()
                if remaining and not remaining.startswith('}'):
                    result.append('\n')

            result.append('    ' * indent + '}\n')
            last_was_closing_brace = True
            i += 1
            continue

        # 键 = 值 / 键 >= 值 / 键 <= 值 / 键 < 值 / 键 > 值
        if i + 1 < len(tokens) and tokens[i + 1] in {'=', '>=', '<=', '<', '>'}:
            key = token
            operator = tokens[i + 1]
            i += 2

            # 收集值，直到下一个键/运算符/花括号
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

            # 如果下一个是 {，不换行（会在 { 处理时接上）
            if i < len(tokens) and tokens[i] == '{':
                continue

        else:
            # 孤立 token（例如单独的 min_distance）
            result.append('    ' * indent + token + '\n')
            last_was_closing_brace = False
            i += 1

    output = ''.join(result).rstrip('\n')

    # 清理过多连续空行
    output = re.sub(r'\n{3,}', '\n\n', output)
    output = output.rstrip() + '\n'

    return output


# ---------- GUI 部分 ----------
def format_compact():
    """压缩格式化"""
    input_text = input_textbox.get("1.0", tk.END).strip()
    if not input_text:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
        return
    try:
        result = compact_stellaris_script(input_text)
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, result)
    except Exception as e:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, f"压缩出错：{e}")


def format_pretty():
    """美化格式化"""
    input_text = input_textbox.get("1.0", tk.END).strip()
    if not input_text:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, "请在输入框中粘贴内容。")
        return
    try:
        result = pretty_format_stellaris_script(input_text)
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, result)
    except Exception as e:
        output_textbox.delete("1.0", tk.END)
        output_textbox.insert(tk.END, f"美化出错：{e}")


# 创建主窗口
root = tk.Tk()
root.title("Stellaris 脚本格式化工具")
root.geometry("800x600")

# 输入区域
tk.Label(root, text="输入原始脚本：", anchor="w").pack(fill="x", padx=5, pady=(5,0))
input_textbox = scrolledtext.ScrolledText(root, height=15, font=("Consolas", 10))
input_textbox.pack(fill="both", expand=True, padx=5, pady=5)

# 按钮框架
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

compact_btn = tk.Button(button_frame, text="转化为指令", command=format_compact, bg="#4CAF50", fg="white", width=15)
compact_btn.pack(side="left", padx=5)

pretty_btn = tk.Button(button_frame, text="指令格式化", command=format_pretty, bg="#2196F3", fg="white", width=15)
pretty_btn.pack(side="left", padx=5)

# 输出区域
tk.Label(root, text="格式化结果：", anchor="w").pack(fill="x", padx=5, pady=(5,0))
output_textbox = scrolledtext.ScrolledText(root, height=15, font=("Consolas", 10))
output_textbox.pack(fill="both", expand=True, padx=5, pady=5)

# 启动消息循环
root.mainloop()