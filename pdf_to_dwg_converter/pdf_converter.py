#!/usr/bin/env python3
"""
PDF工程图转DWG转换器
高精度矢量转换，保留线条和文字
"""

import pdfplumber
import ezdxf
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np


class PDFToDWGConverter:
    """PDF转DWG转换器"""
    
    def __init__(self):
        self.lines = []
        self.texts = []
        self.curves = []
    
    def extract_lines(self, pdf_path: str, page_num: int = 0) -> List[Dict]:
        """
        提取PDF中的矢量线条
        
        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从0开始）
        
        Returns:
            线条列表，每条线包含起点和终点坐标
        """
        lines = []
        
        with pdfplumber.open(pdf_path) as pdf:
            if page_num >= len(pdf.pages):
                return []
            
            page = pdf.pages[page_num]
            
            # 提取线条
            for line in page.lines:
                x1 = line['x0'] * 25.4 / 72  # pt to mm
                y1 = line['y0'] * 25.4 / 72
                x2 = line['x1'] * 25.4 / 72
                y2 = line['y1'] * 25.4 / 72
                
                lines.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'type': 'line'
                })
            
            # 提取矩形（转换为线条）
            for rect in page.rects:
                x0 = rect['x0'] * 25.4 / 72
                y0 = rect['y0'] * 25.4 / 72
                x1 = rect['x1'] * 25.4 / 72
                y1 = rect['y1'] * 25.4 / 72
                
                # 矩形四条边
                lines.extend([
                    {'x1': x0, 'y1': y0, 'x2': x1, 'y2': y0, 'type': 'rect'},
                    {'x1': x1, 'y1': y0, 'x2': x1, 'y2': y1, 'type': 'rect'},
                    {'x1': x1, 'y1': y1, 'x2': x0, 'y2': y1, 'type': 'rect'},
                    {'x1': x0, 'y1': y1, 'x2': x0, 'y2': y0, 'type': 'rect'}
                ])
        
        return lines
    
    def extract_text(self, pdf_path: str, page_num: int = 0) -> List[Dict]:
        """
        提取PDF中的文字
        
        Args:
            pdf_path: PDF文件路径
            page_num: 页码
        
        Returns:
            文字列表，包含内容、位置和样式
        """
        texts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            if page_num >= len(pdf.pages):
                return []
            
            page = pdf.pages[page_num]
            chars = page.chars
            
            if not chars:
                return []
            
            # 按Y坐标聚类（同一行的文字）
            y_groups = {}
            tolerance = 1.5  # pt
            
            for char in chars:
                y = char['y0']
                found_group = False
                
                for group_y in y_groups:
                    if abs(y - group_y) < tolerance:
                        y_groups[group_y].append(char)
                        found_group = True
                        break
                
                if not found_group:
                    y_groups[y] = [char]
            
            # 处理每行文字
            for y, chars_in_line in sorted(y_groups.items()):
                # 按X坐标排序
                chars_in_line.sort(key=lambda c: c['x0'])
                
                # 合并连续文字
                text_parts = []
                current_part = {'text': chars_in_line[0]['text'], 'x0': chars_in_line[0]['x0']}
                
                for i in range(1, len(chars_in_line)):
                    prev_char = chars_in_line[i-1]
                    curr_char = chars_in_line[i]
                    
                    # 检查间距（超过2.5倍字距认为是不同段）
                    gap = curr_char['x0'] - prev_char['x1']
                    avg_width = (prev_char['width'] + curr_char['width']) / 2
                    
                    if gap > avg_width * 2.5:
                        # 新段落
                        text_parts.append(current_part)
                        current_part = {'text': curr_char['text'], 'x0': curr_char['x0']}
                    else:
                        current_part['text'] += curr_char['text']
                
                text_parts.append(current_part)
                
                # 添加到结果
                for part in text_parts:
                    texts.append({
                        'text': part['text'],
                        'x': part['x0'] * 25.4 / 72,
                        'y': y * 25.4 / 72,
                        'height': chars_in_line[0]['height'] * 25.4 / 72
                    })
        
        return texts
    
    def convert_page(self, pdf_path: str, output_path: str, page_num: int = 0) -> bool:
        """
        转换单页PDF为DWG
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出DWG文件路径
            page_num: 页码
        
        Returns:
            是否成功
        """
        try:
            # 提取线条
            lines = self.extract_lines(pdf_path, page_num)
            
            # 提取文字
            texts = self.extract_text(pdf_path, page_num)
            
            # 创建DXF
            doc = ezdxf.new('R2018')
            msp = doc.modelspace()
            
            # 添加线条
            for line in lines:
                msp.add_line(
                    (line['x1'], line['y1']),
                    (line['x2'], line['y2'])
                )
            
            # 添加文字
            for text in texts:
                msp.add_text(
                    text['text'],
                    height=text['height'],
                    dxfattribs={'insert': (text['x'], text['y'])}
                )
            
            # 保存DXF
            doc.saveas(output_path)
            
            return True
            
        except Exception as e:
            print(f"转换失败: {e}")
            return False
    
    def convert_all_pages(self, pdf_path: str, output_dir: str) -> List[str]:
        """
        转换所有页面
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
        
        Returns:
            生成的文件列表
        """
        output_files = []
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with pdfplumber.open(pdf_path) as pdf:
            for i in range(len(pdf.pages)):
                output_path = output_dir / f"page_{i+1:03d}.dxf"
                
                if self.convert_page(pdf_path, str(output_path), i):
                    output_files.append(str(output_path))
                    print(f"✓ 第{i+1}页转换完成: {output_path}")
                else:
                    print(f"✗ 第{i+1}页转换失败")
        
        return output_files


# 便捷函数
def pdf_to_dwg(pdf_path: str, output_path: Optional[str] = None) -> bool:
    """
    便捷函数：PDF转DWG
    
    Args:
        pdf_path: PDF文件路径
        output_path: 输出路径（可选，默认为同名.dxf）
    
    Returns:
        是否成功
    """
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.dxf'))
    
    converter = PDFToDWGConverter()
    return converter.convert_page(pdf_path, output_path)


def batch_convert(pdf_path: str, output_dir: str) -> List[str]:
    """
    批量转换所有页面
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
    
    Returns:
        生成的文件列表
    """
    converter = PDFToDWGConverter()
    return converter.convert_all_pages(pdf_path, output_dir)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_converter.py <PDF文件> [输出目录]")
        print("示例: python pdf_converter.py 图纸.pdf output/")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    print(f"正在转换: {pdf_file}")
    files = batch_convert(pdf_file, output_dir)
    
    print(f"\n转换完成！共生成 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f}")
