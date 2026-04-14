#!/usr/bin/env python3
"""
CAD图纸批量处理器 - 使用示例
"""

from cad_processor import CADProcessor, extract_color, batch_extract_color
import glob
import os


def example_single_file():
    """示例1: 单文件提取"""
    print("=== 示例1: 单文件提取 ===")
    
    # 提取颜色30的实体
    input_file = "D:/工作/西宁站改/西宁动车所改扩建工程及西宁站东端联络线平面布置图.dwg"
    output_file = "D:/输出/环场道路_色号30.dwg"
    color = 30
    
    if os.path.exists(input_file):
        success = extract_color(input_file, color, output_file)
        print(f"提取{'成功' if success else '失败'}: {output_file}")
    else:
        print(f"输入文件不存在: {input_file}")


def example_batch_process():
    """示例2: 批量处理"""
    print("\n=== 示例2: 批量处理 ===")
    
    # 获取所有DWG文件
    input_dir = "D:/工作/西宁站改/测量员"
    output_dir = "D:/输出/提取结果"
    color = 30
    
    if os.path.exists(input_dir):
        files = glob.glob(os.path.join(input_dir, "*.dwg"))
        print(f"找到 {len(files)} 个文件")
        
        results = batch_extract_color(files, color, output_dir)
        
        print(f"成功: {len(results['success'])} 个")
        print(f"失败: {len(results['failed'])} 个")
        
        if results['failed']:
            print("失败的文件:")
            for f in results['failed']:
                print(f"  - {f}")
    else:
        print(f"输入目录不存在: {input_dir}")


def example_advanced():
    """示例3: 高级用法"""
    print("\n=== 示例3: 高级用法 ===")
    
    # 创建处理器实例
    processor = CADProcessor()
    
    # 指定accoreconsole路径（如果需要）
    # processor = CADProcessor(r"D:\cad2020\AutoCAD 2020\accoreconsole.exe")
    
    input_file = "D:/工作/示例.dwg"
    output_file = "D:/输出/结果.dwg"
    
    if os.path.exists(input_file):
        # 只提取特定类型的实体
        entity_types = ['LINE', 'LWPOLYLINE', 'CIRCLE']
        
        success = processor.extract_by_color(
            input_file=input_file,
            color=30,
            output_file=output_file,
            entity_types=entity_types
        )
        
        print(f"提取{'成功' if success else '失败'}")
    else:
        print(f"示例文件不存在，请修改路径")


def example_check_setup():
    """示例4: 检查环境设置"""
    print("\n=== 示例4: 环境检查 ===")
    
    try:
        processor = CADProcessor()
        print(f"✓ 找到accoreconsole: {processor.accoreconsole}")
    except FileNotFoundError as e:
        print(f"✗ {e}")
        print("  请检查AutoCAD是否正确安装")


if __name__ == "__main__":
    # 运行示例
    example_check_setup()
    
    # 取消注释以运行其他示例
    # example_single_file()
    # example_batch_process()
    # example_advanced()
    
    print("\n提示: 修改示例中的文件路径后，取消注释即可运行")
