#!/usr/bin/env python3
"""
CAD图纸批量处理器
支持按颜色提取实体、线宽调整等功能
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Union


class CADProcessor:
    """CAD图纸处理器"""
    
    def __init__(self, accoreconsole_path: Optional[str] = None):
        """
        初始化处理器
        
        Args:
            accoreconsole_path: AutoCAD Core Console路径，默认使用常见位置
        """
        if accoreconsole_path:
            self.accoreconsole = accoreconsole_path
        else:
            # 尝试常见安装路径
            possible_paths = [
                r"C:\Program Files\Autodesk\AutoCAD 2020\accoreconsole.exe",
                r"C:\Program Files\Autodesk\AutoCAD 2021\accoreconsole.exe",
                r"C:\Program Files\Autodesk\AutoCAD 2022\accoreconsole.exe",
                r"C:\Program Files\Autodesk\AutoCAD 2023\accoreconsole.exe",
                r"D:\cad2020\AutoCAD 2020\accoreconsole.exe",
            ]
            self.accoreconsole = None
            for path in possible_paths:
                if os.path.exists(path):
                    self.accoreconsole = path
                    break
            
            if not self.accoreconsole:
                raise FileNotFoundError("未找到accoreconsole.exe，请手动指定路径")
    
    def extract_by_color(self, 
                         input_file: str, 
                         color: int, 
                         output_file: str,
                         entity_types: Optional[List[str]] = None) -> bool:
        """
        按颜色提取实体
        
        Args:
            input_file: 输入DWG文件路径
            color: 颜色号 (1-255)
            output_file: 输出DWG文件路径
            entity_types: 实体类型列表，如 ['LINE', 'CIRCLE', 'LWPOLYLINE']
        
        Returns:
            bool: 是否成功
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        # 创建工作目录
        work_dir = tempfile.mkdtemp()
        try:
            # 复制输入文件到工作目录
            work_input = os.path.join(work_dir, "input.dwg")
            shutil.copy2(input_file, work_input)
            
            # 生成LISP脚本
            lisp_script = self._generate_extract_lisp(color, entity_types)
            lisp_file = os.path.join(work_dir, "extract.lsp")
            with open(lisp_file, 'w', encoding='utf-8') as f:
                f.write(lisp_script)
            
            # 执行处理
            result = self._run_accoreconsole(work_input, lisp_file)
            
            if result and os.path.exists(work_input):
                # 复制结果到输出路径
                shutil.copy2(work_input, output_file)
                return True
            
            return False
            
        finally:
            # 清理工作目录
            shutil.rmtree(work_dir, ignore_errors=True)
    
    def batch_extract(self,
                      input_files: List[str],
                      color: int,
                      output_dir: str,
                      entity_types: Optional[List[str]] = None) -> dict:
        """
        批量按颜色提取
        
        Args:
            input_files: 输入文件列表
            color: 颜色号
            output_dir: 输出目录
            entity_types: 实体类型列表
        
        Returns:
            dict: 处理结果统计
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            'success': [],
            'failed': [],
            'total': len(input_files)
        }
        
        for input_file in input_files:
            filename = os.path.basename(input_file)
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}_color{color}{ext}")
            
            try:
                if self.extract_by_color(input_file, color, output_file, entity_types):
                    results['success'].append(filename)
                else:
                    results['failed'].append(filename)
            except Exception as e:
                results['failed'].append(f"{filename}: {str(e)}")
        
        return results
    
    def adjust_linewidth(self,
                         input_file: str,
                         output_file: str,
                         width_mapping: Optional[dict] = None) -> bool:
        """
        调整线宽
        
        Args:
            input_file: 输入DWG文件
            output_file: 输出DWG文件
            width_mapping: 线宽映射，如 {0: 0.25, 1: 0.5}
        
        Returns:
            bool: 是否成功
        """
        # 实现线宽调整逻辑
        # 这里可以添加具体的线宽处理代码
        pass
    
    def _generate_extract_lisp(self, color: int, entity_types: Optional[List[str]]) -> str:
        """生成提取LISP脚本"""
        
        # 基础LISP脚本
        lisp_code = f"""; CAD Batch Processor - Extract by Color
(defun c:ExtractByColor ()
  (setq old_cmdecho (getvar "CMDECHO"))
  (setvar "CMDECHO" 0)
  
  ; 选择颜色为{color}的实体
  (setq ss (ssget "_X" '((62 . {color}))))
  
  (if ss
    (progn
      ; 反选并删除其他实体
      (command "_.SELECT" "_ALL" "_R" ss "")
      (command "_.ERASE" "_P" "")
      (command "_.SAVEAS" "AC1018" "input.dwg" "")
      (princ (strcat "\\n提取完成，共 " (itoa (sslength ss)) " 个实体"))
    )
    (princ "\\n未找到指定颜色的实体")
  )
  
  (setvar "CMDECHO" old_cmdecho)
  (princ)
)

; 自动执行
(ExtractByColor)
"""
        return lisp_code
    
    def _run_accoreconsole(self, dwg_file: str, lisp_file: str) -> bool:
        """运行accoreconsole执行LISP脚本"""
        try:
            cmd = [
                self.accoreconsole,
                "/i", dwg_file,
                "/s", lisp_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("处理超时")
            return False
        except Exception as e:
            print(f"执行错误: {e}")
            return False


# 便捷函数
def extract_color(input_file: str, color: int, output_file: str) -> bool:
    """便捷函数：提取指定颜色实体"""
    processor = CADProcessor()
    return processor.extract_by_color(input_file, color, output_file)


def batch_extract_color(input_files: List[str], color: int, output_dir: str) -> dict:
    """便捷函数：批量提取"""
    processor = CADProcessor()
    return processor.batch_extract(input_files, color, output_dir)


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) < 4:
        print("用法: python cad_processor.py <输入文件> <颜色号> <输出文件>")
        print("示例: python cad_processor.py 平面图.dwg 30 提取结果.dwg")
        sys.exit(1)
    
    input_file = sys.argv[1]
    color = int(sys.argv[2])
    output_file = sys.argv[3]
    
    if extract_color(input_file, color, output_file):
        print(f"提取成功: {output_file}")
    else:
        print("提取失败")
        sys.exit(1)
