#!/usr/bin/env python
# -*- coding: utf-8 -*-

def check_indentation():
    try:
        # 读取文件内容
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试编译代码
        try:
            compile(content, 'app.py', 'exec')
            print("文件编译成功，没有语法错误。")
            return True
        except IndentationError as e:
            print(f"缩进错误: {e}")
            
            # 获取错误行号
            error_line = e.lineno
            print(f"缩进错误在第 {error_line} 行")
            
            # 读取文件内容（按行）
            with open('app.py', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 显示错误行及其前后几行
            start_line = max(0, error_line - 5)
            end_line = min(len(lines), error_line + 5)
            
            print("\n问题区域:")
            for i in range(start_line, end_line):
                prefix = ">>> " if i + 1 == error_line else "    "
                print(f"{prefix}{i+1}: {lines[i].rstrip()}")
            
            # 检查缩进级别
            if error_line > 0 and error_line <= len(lines):
                problem_line = lines[error_line - 1]
                leading_spaces = len(problem_line) - len(problem_line.lstrip())
                print(f"\n问题行缩进: {leading_spaces} 个空格")
                
                # 检查前一行缩进
                if error_line > 1:
                    prev_line = lines[error_line - 2]
                    prev_leading_spaces = len(prev_line) - len(prev_line.lstrip())
                    print(f"前一行缩进: {prev_leading_spaces} 个空格")
                    
                    # 如果缩进不匹配，提供修复建议
                    if abs(leading_spaces - prev_leading_spaces) % 4 != 0:
                        print(f"缩进不匹配！建议将第 {error_line} 行的缩进调整为 {prev_leading_spaces} 个空格")
            
            return False
        except SyntaxError as e:
            print(f"语法错误: {e}")
            print(f"错误位置: 第 {e.lineno} 行，第 {e.offset} 列")
            return False
    except Exception as e:
        print(f"检查过程中出错: {e}")
        return False

if __name__ == "__main__":
    check_indentation()
    
    # 如果检查成功，尝试运行Flask应用
    import subprocess
    print("\n尝试运行Flask应用...")
    result = subprocess.run(['flask', '--debug', 'run'], capture_output=True, text=True)
    if result.returncode != 0:
        print("运行失败:")
        print(result.stderr)
    else:
        print("Flask应用启动成功！") 