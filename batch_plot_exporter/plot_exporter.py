#!/usr/bin/env python3
"""
CAD批量出图工具
自动打印/导出DWG为PDF/图片
"""

import win32com.client
import os
from pathlib import Path
from typing import List, Optional, Dict
import time


class BatchPlotExporter:
    """CAD批量出图工具"""
    
    def __init__(self):
        self.acad = None
        self.doc = None
    
    def connect_autocad(self):
        """连接AutoCAD"""
        try:
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acad.Visible = True
            return True
        except Exception as e:
            print(f"连接AutoCAD失败: {e}")
            return False
    
    def open_dwg(self, file_path: str) -> bool:
        """打开DWG文件"""
        try:
            self.doc = self.acad.Documents.Open(file_path)
            time.sleep(2)  # 等待文件加载
            return True
        except Exception as e:
            print(f"打开文件失败: {e}")
            return False
    
    def get_layouts(self) -> List[str]:
        """获取所有布局名称"""
        layouts = []
        try:
            for layout in self.doc.Layouts:
                if layout.Name != "Model":  # 排除模型空间
                    layouts.append(layout.Name)
        except:
            pass
        return layouts
    
    def export_layout_to_pdf(self, layout_name: str, output_path: str, 
                            plot_style: Optional[str] = None) -> bool:
        """
        导出布局为PDF
        
        Args:
            layout_name: 布局名称
            output_path: 输出PDF路径
            plot_style: 打印样式表（可选）
        
        Returns:
            是否成功
        """
        try:
            # 切换到指定布局
            layout = self.doc.Layouts.Item(layout_name)
            self.doc.ActiveLayout = layout
            
            # 设置打印配置
            layout.ConfigName = "DWG To PDF.pc3"
            layout.PlotWithLineweights = True
            layout.PlotPlotStyles = True
            
            if plot_style:
                layout.StyleSheet = plot_style
            
            # 设置输出路径
            layout.PlotType = 1  # acLayout
            
            # 执行打印
            self.doc.Plot.PlotToFile(output_path, layout.ConfigName)
            
            return True
            
        except Exception as e:
            print(f"导出PDF失败: {e}")
            return False
    
    def export_model_to_pdf(self, output_path: str, 
                           plot_area: Optional[Dict] = None,
                           scale: float = 1.0) -> bool:
        """
        导出模型空间为PDF
        
        Args:
            output_path: 输出PDF路径
            plot_area: 打印区域 {x1, y1, x2, y2}
            scale: 出图比例
        
        Returns:
            是否成功
        """
        try:
            # 切换到模型空间
            self.doc.ActiveSpace = 0  # acModelSpace
            
            # 获取模型空间布局
            layout = self.doc.Layouts.Item("Model")
            
            # 设置打印配置
            layout.ConfigName = "DWG To PDF.pc3"
            layout.PlotWithLineweights = True
            layout.PlotPlotStyles = True
            
            # 设置打印区域
            if plot_area:
                layout.SetWindowToPlot(
                    (plot_area['x1'], plot_area['y1']),
                    (plot_area['x2'], plot_area['y2'])
                )
                layout.PlotType = 2  # acWindow
            else:
                layout.PlotType = 4  # acExtents
            
            # 设置比例
            layout.StandardScale = 0  # acScaleToFit
            layout.UseStandardScale = True
            
            # 执行打印
            self.doc.Plot.PlotToFile(output_path, layout.ConfigName)
            
            return True
            
        except Exception as e:
            print(f"导出模型空间失败: {e}")
            return False
    
    def batch_export_layouts(self, output_dir: str, 
                            prefix: str = "") -> List[str]:
        """
        批量导出所有布局
        
        Args:
            output_dir: 输出目录
            prefix: 文件名前缀
        
        Returns:
            生成的文件列表
        """
        output_files = []
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        layouts = self.get_layouts()
        
        for layout_name in layouts:
            # 清理文件名
            safe_name = "".join(c for c in layout_name if c.isalnum() or c in (' ', '-', '_')).strip()
            output_path = output_dir / f"{prefix}{safe_name}.pdf"
            
            if self.export_layout_to_pdf(layout_name, str(output_path)):
                output_files.append(str(output_path))
                print(f"✓ 导出完成: {layout_name} -> {output_path.name}")
            else:
                print(f"✗ 导出失败: {layout_name}")
        
        return output_files
    
    def close_dwg(self, save: bool = False):
        """关闭DWG文件"""
        try:
            if self.doc:
                self.doc.Close(save)
                self.doc = None
        except:
            pass
    
    def quit_autocad(self):
        """退出AutoCAD"""
        try:
            if self.acad:
                self.acad.Quit()
                self.acad = None
        except:
            pass


# 便捷函数
def export_dwg_to_pdf(dwg_path: str, output_dir: str, 
                     export_layouts: bool = True,
                     export_model: bool = False) -> List[str]:
    """
    便捷函数：导出DWG为PDF
    
    Args:
        dwg_path: DWG文件路径
        output_dir: 输出目录
        export_layouts: 是否导出布局
        export_model: 是否导出模型空间
    
    Returns:
        生成的文件列表
    """
    exporter = BatchPlotExporter()
    output_files = []
    
    try:
        # 连接AutoCAD
        if not exporter.connect_autocad():
            return []
        
        # 打开文件
        if not exporter.open_dwg(dwg_path):
            return []
        
        # 获取文件名前缀
        prefix = Path(dwg_path).stem + "_"
        
        # 导出布局
        if export_layouts:
            files = exporter.batch_export_layouts(output_dir, prefix)
            output_files.extend(files)
        
        # 导出模型空间
        if export_model:
            output_path = Path(output_dir) / f"{prefix}Model.pdf"
            if exporter.export_model_to_pdf(str(output_path)):
                output_files.append(str(output_path))
                print(f"✓ 导出模型空间: {output_path.name}")
        
    finally:
        exporter.close_dwg(save=False)
        exporter.quit_autocad()
    
    return output_files


def batch_export_directory(input_dir: str, output_dir: str) -> Dict[str, List[str]]:
    """
    批量处理整个目录
    
    Args:
        input_dir: 输入目录（包含DWG文件）
        output_dir: 输出目录
    
    Returns:
        每个文件的处理结果
    """
    results = {}
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有DWG文件
    dwg_files = list(input_dir.glob("**/*.dwg"))
    
    print(f"找到 {len(dwg_files)} 个DWG文件")
    
    for dwg_file in dwg_files:
        print(f"\n处理: {dwg_file.name}")
        files = export_dwg_to_pdf(str(dwg_file), str(output_dir))
        results[dwg_file.name] = files
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python plot_exporter.py <DWG文件> [输出目录]")
        print("  python plot_exporter.py --batch <输入目录> <输出目录>")
        print("\n示例:")
        print("  python plot_exporter.py 图纸.dwg output/")
        print("  python plot_exporter.py --batch dwg_files/ pdf_output/")
        sys.exit(1)
    
    if sys.argv[1] == "--batch":
        # 批量模式
        if len(sys.argv) < 4:
            print("批量模式需要输入目录和输出目录")
            sys.exit(1)
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3]
        
        print(f"批量处理: {input_dir} -> {output_dir}")
        results = batch_export_directory(input_dir, output_dir)
        
        print(f"\n处理完成!")
        for dwg, files in results.items():
            print(f"  {dwg}: {len(files)} 个PDF")
    
    else:
        # 单文件模式
        dwg_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
        
        print(f"处理: {dwg_file}")
        files = export_dwg_to_pdf(dwg_file, output_dir)
        
        print(f"\n生成 {len(files)} 个PDF文件:")
        for f in files:
            print(f"  - {f}")
