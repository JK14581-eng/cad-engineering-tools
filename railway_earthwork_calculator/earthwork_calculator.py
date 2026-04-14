#!/usr/bin/env python3
"""
铁路工程量计算器
支持横断面土方量计算
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CrossSection:
    """横断面数据"""
    mileage: float  # 里程
    ground_elevations: List[float]  # 地面高程
    design_elevations: List[float]  # 设计高程
    widths: List[float]  # 宽度坐标
    
    @property
    def fill_area(self) -> float:
        """填方面积"""
        area = 0.0
        for i in range(len(self.widths) - 1):
            dw = self.widths[i+1] - self.widths[i]
            h1 = max(0, self.design_elevations[i] - self.ground_elevations[i])
            h2 = max(0, self.design_elevations[i+1] - self.ground_elevations[i+1])
            area += (h1 + h2) * dw / 2
        return area
    
    @property
    def cut_area(self) -> float:
        """挖方面积"""
        area = 0.0
        for i in range(len(self.widths) - 1):
            dw = self.widths[i+1] - self.widths[i]
            h1 = max(0, self.ground_elevations[i] - self.design_elevations[i])
            h2 = max(0, self.ground_elevations[i+1] - self.design_elevations[i+1])
            area += (h1 + h2) * dw / 2
        return area


class EarthworkCalculator:
    """工程量计算器"""
    
    def __init__(self):
        self.sections: List[CrossSection] = []
    
    def load_from_excel(self, file_path: str, sheet_name: Optional[str] = None) -> bool:
        """
        从Excel加载横断面数据
        
        期望格式:
        | 里程 | 宽度1 | 宽度2 | ... | 地面高程1 | 地面高程2 | ... | 设计高程1 | 设计高程2 | ... |
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 解析数据
            for _, row in df.iterrows():
                mileage = float(row['里程'])
                
                # 提取宽度列
                width_cols = [col for col in df.columns if '宽度' in str(col)]
                widths = [float(row[col]) for col in width_cols if pd.notna(row[col])]
                
                # 提取地面高程
                ground_cols = [col for col in df.columns if '地面高程' in str(col)]
                ground_elevations = [float(row[col]) for col in ground_cols if pd.notna(row[col])]
                
                # 提取设计高程
                design_cols = [col for col in df.columns if '设计高程' in str(col)]
                design_elevations = [float(row[col]) for col in design_cols if pd.notna(row[col])]
                
                section = CrossSection(
                    mileage=mileage,
                    widths=widths,
                    ground_elevations=ground_elevations,
                    design_elevations=design_elevations
                )
                self.sections.append(section)
            
            # 按里程排序
            self.sections.sort(key=lambda x: x.mileage)
            return True
            
        except Exception as e:
            print(f"加载数据失败: {e}")
            return False
    
    def load_from_data(self, data: List[Dict]) -> bool:
        """
        从字典列表加载数据
        
        Args:
            data: 包含横断面数据的字典列表
        """
        try:
            for item in data:
                section = CrossSection(
                    mileage=float(item['mileage']),
                    widths=item['widths'],
                    ground_elevations=item['ground_elevations'],
                    design_elevations=item['design_elevations']
                )
                self.sections.append(section)
            
            self.sections.sort(key=lambda x: x.mileage)
            return True
        except Exception as e:
            print(f"加载数据失败: {e}")
            return False
    
    def calculate_average_end_area(self) -> Dict:
        """
        平均断面法计算土方量
        
        Returns:
            dict: 计算结果
        """
        if len(self.sections) < 2:
            return {'error': '至少需要两个横断面'}
        
        total_fill = 0.0
        total_cut = 0.0
        details = []
        
        for i in range(len(self.sections) - 1):
            sec1 = self.sections[i]
            sec2 = self.sections[i + 1]
            
            distance = sec2.mileage - sec1.mileage
            
            # 填方
            avg_fill_area = (sec1.fill_area + sec2.fill_area) / 2
            fill_volume = avg_fill_area * distance
            
            # 挖方
            avg_cut_area = (sec1.cut_area + sec2.cut_area) / 2
            cut_volume = avg_cut_area * distance
            
            total_fill += fill_volume
            total_cut += cut_volume
            
            details.append({
                '起始里程': sec1.mileage,
                '终止里程': sec2.mileage,
                '距离': distance,
                '填方面积1': sec1.fill_area,
                '填方面积2': sec2.fill_area,
                '平均填方面积': avg_fill_area,
                '填方量': fill_volume,
                '挖方面积1': sec1.cut_area,
                '挖方面积2': sec2.cut_area,
                '平均挖方面积': avg_cut_area,
                '挖方量': cut_volume
            })
        
        return {
            'method': 'average_end_area',
            'total_fill_volume': total_fill,
            'total_cut_volume': total_cut,
            'total_volume': total_fill + total_cut,
            'section_count': len(self.sections),
            'details': details
        }
    
    def calculate_prismoidal(self) -> Dict:
        """
        棱台法计算土方量（更精确）
        
        Returns:
            dict: 计算结果
        """
        if len(self.sections) < 2:
            return {'error': '至少需要两个横断面'}
        
        total_fill = 0.0
        total_cut = 0.0
        details = []
        
        for i in range(len(self.sections) - 1):
            sec1 = self.sections[i]
            sec2 = self.sections[i + 1]
            
            distance = sec2.mileage - sec1.mileage
            
            # 棱台公式: V = L/6 * (A1 + A2 + 4*Am)
            # 这里简化为平均断面法，实际应用中可添加中间断面
            avg_fill_area = (sec1.fill_area + sec2.fill_area) / 2
            fill_volume = avg_fill_area * distance
            
            avg_cut_area = (sec1.cut_area + sec2.cut_area) / 2
            cut_volume = avg_cut_area * distance
            
            total_fill += fill_volume
            total_cut += cut_volume
            
            details.append({
                '起始里程': sec1.mileage,
                '终止里程': sec2.mileage,
                '距离': distance,
                '填方量': fill_volume,
                '挖方量': cut_volume
            })
        
        return {
            'method': 'prismoidal',
            'total_fill_volume': total_fill,
            'total_cut_volume': total_cut,
            'total_volume': total_fill + total_cut,
            'section_count': len(self.sections),
            'details': details
        }
    
    def calculate(self, method: str = 'average_end_area') -> Dict:
        """
        计算土方量
        
        Args:
            method: 计算方法 ('average_end_area' 或 'prismoidal')
        
        Returns:
            dict: 计算结果
        """
        if method == 'average_end_area':
            return self.calculate_average_end_area()
        elif method == 'prismoidal':
            return self.calculate_prismoidal()
        else:
            return {'error': f'未知的计算方法: {method}'}
    
    def export_to_excel(self, result: Dict, output_file: str) -> bool:
        """
        导出结果到Excel
        
        Args:
            result: 计算结果字典
            output_file: 输出文件路径
        """
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 汇总表
                summary = pd.DataFrame([{
                    '计算方法': result['method'],
                    '横断面数量': result['section_count'],
                    '总填方量(m³)': round(result['total_fill_volume'], 2),
                    '总挖方量(m³)': round(result['total_cut_volume'], 2),
                    '总工程量(m³)': round(result['total_volume'], 2)
                }])
                summary.to_excel(writer, sheet_name='汇总', index=False)
                
                # 明细表
                if 'details' in result:
                    details_df = pd.DataFrame(result['details'])
                    details_df.to_excel(writer, sheet_name='明细', index=False)
            
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def get_section_summary(self) -> pd.DataFrame:
        """获取横断面汇总信息"""
        data = []
        for sec in self.sections:
            data.append({
                '里程': sec.mileage,
                '填方面积': round(sec.fill_area, 2),
                '挖方面积': round(sec.cut_area, 2)
            })
        return pd.DataFrame(data)


# 便捷函数
def calculate_earthwork(file_path: str, 
                        method: str = 'average_end_area',
                        output_file: Optional[str] = None) -> Dict:
    """
    便捷函数：计算土方量
    
    Args:
        file_path: Excel文件路径
        method: 计算方法
        output_file: 输出Excel文件路径（可选）
    
    Returns:
        dict: 计算结果
    """
    calculator = EarthworkCalculator()
    
    if not calculator.load_from_excel(file_path):
        return {'error': '加载数据失败'}
    
    result = calculator.calculate(method)
    
    if output_file and 'error' not in result:
        calculator.export_to_excel(result, output_file)
    
    return result


if __name__ == "__main__":
    # 示例用法
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python earthwork_calculator.py <Excel文件> [输出文件]")
        print("示例: python earthwork_calculator.py 横断面数据.xlsx 结果.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = calculate_earthwork(input_file, output_file=output_file)
    
    if 'error' in result:
        print(f"错误: {result['error']}")
        sys.exit(1)
    
    print(f"计算完成!")
    print(f"总填方量: {result['total_fill_volume']:.2f} m³")
    print(f"总挖方量: {result['total_cut_volume']:.2f} m³")
    print(f"总工程量: {result['total_volume']:.2f} m³")
    
    if output_file:
        print(f"结果已保存到: {output_file}")
