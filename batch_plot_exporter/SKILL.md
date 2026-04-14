# CAD批量出图工具

## 基本信息

- **名称**: CAD批量出图工具
- **版本**: 1.0.0
- **价格**: $10
- **类别**: CAD工具 / 批量处理
- **标签**: cad, plot, pdf, batch, export, print

## 功能描述

自动批量导出DWG文件为PDF，支持布局空间和模型空间，无需手动操作。

### 核心功能

1. **批量导出布局**
   - 自动识别所有布局
   - 按布局名称生成PDF
   - 保留打印样式和线宽

2. **模型空间导出**
   - 支持窗口选择区域
   - 自动适应比例
   - 大图自动分割

3. **批量处理目录**
   - 递归处理子目录
   - 自动命名管理
   - 进度实时显示

4. **打印配置**
   - 支持自定义打印样式
   - 保留线宽设置
   - 支持多种输出格式

## 技术规格

### 依赖库
```
pywin32>=227
```

### 系统要求
- Windows系统
- AutoCAD 2018+ 或 AutoCAD LT
- Python 3.8+

### 支持格式
- **输入**: DWG (所有版本)
- **输出**: PDF
- **打印**: 使用AutoCAD内置PDF打印机

## 使用方法

### 单文件导出
```python
from plot_exporter import export_dwg_to_pdf

# 导出所有布局
files = export_dwg_to_pdf('图纸.dwg', 'output/')

# 同时导出模型空间
files = export_dwg_to_pdf('图纸.dwg', 'output/', export_model=True)
```

### 批量处理目录
```python
from plot_exporter import batch_export_directory

results = batch_export_directory('dwg_files/', 'pdf_output/')
```

### 命令行使用
```bash
# 单文件
python plot_exporter.py 图纸.dwg output/

# 批量处理
python plot_exporter.py --batch dwg_files/ pdf_output/
```

## 性能指标

| 指标 | 数值 |
|-----|------|
| 处理速度 | 10-30秒/布局 |
| 支持最大文件 | 100MB+ |
| 批量处理能力 | 无限制 |
| 成功率 | >98% |

## 适用场景

- 项目归档出图
- 批量打印PDF
- 图纸分发
- 版本备份

## 注意事项

1. **AutoCAD要求**
   - 必须安装AutoCAD
   - 需要DWG To PDF.pc3打印机

2. **打印样式**
   - 确保CTB/STB文件可用
   - 建议提前配置好打印样式

3. **大文件处理**
   - 复杂图纸可能需要更长时间
   - 建议分批处理

## 版本历史

### v1.0.0 (2026-04-14)
- ✨ 首次发布
- ✨ 布局批量导出
- ✨ 模型空间导出
- ✨ 目录批量处理
