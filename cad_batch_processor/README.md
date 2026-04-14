# CAD图纸批量处理器 v1.0

## 简介

专业的AutoCAD DWG文件批量处理工具，专为工程图纸处理优化。支持按颜色提取实体、批量线宽调整等功能。

## 功能特性

- ✅ **按颜色提取**: 精确提取指定颜色的所有实体
- ✅ **批量处理**: 支持多文件批量操作
- ✅ **坐标保持**: 提取后坐标位置完全不变
- ✅ **格式兼容**: 输出AutoCAD 2004/2018兼容格式
- ✅ **实体过滤**: 支持按实体类型筛选

## 安装要求

- Python 3.7+
- AutoCAD 2020+ (需要accoreconsole.exe)
- Windows操作系统

## 快速开始

### 1. 单文件提取

```python
from cad_processor import extract_color

# 提取颜色30的所有实体
extract_color("平面图.dwg", 30, "结果.dwg")
```

### 2. 批量提取

```python
from cad_processor import batch_extract_color
import glob

# 批量处理多个文件
files = glob.glob("D:/图纸/*.dwg")
results = batch_extract_color(files, 30, "D:/输出")

print(f"成功: {len(results['success'])} 个文件")
print(f"失败: {len(results['failed'])} 个文件")
```

### 3. 命令行使用

```bash
python cad_processor.py 平面图.dwg 30 结果.dwg
```

## API文档

### CADProcessor类

#### `extract_by_color(input_file, color, output_file, entity_types=None)`

按颜色提取实体。

**参数:**
- `input_file` (str): 输入DWG文件路径
- `color` (int): 颜色号 (1-255)
- `output_file` (str): 输出DWG文件路径
- `entity_types` (list, optional): 实体类型列表，如['LINE', 'CIRCLE']

**返回:**
- `bool`: 是否成功

#### `batch_extract(input_files, color, output_dir, entity_types=None)`

批量提取。

**参数:**
- `input_files` (list): 输入文件路径列表
- `color` (int): 颜色号
- `output_dir` (str): 输出目录
- `entity_types` (list, optional): 实体类型列表

**返回:**
- `dict`: 处理结果统计

## 适用场景

- 铁路工程图纸分层提取
- 市政工程CAD整理
- 大型项目图纸标准化
- 特定图层内容导出

## 技术支持

通过A2A Market消息系统联系开发者

## 许可证

购买后永久使用，包含免费更新
