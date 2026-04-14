# CAD图纸批量处理器

## 功能描述

专业的AutoCAD DWG文件批量处理工具，支持：
- 按颜色提取特定实体
- 批量线宽调整
- 保持原始坐标不变
- 自动转换为标准DWG格式

## 适用场景

- 铁路工程图纸处理
- 市政工程CAD整理
- 大型项目图纸分层提取
- 图纸标准化处理

## 技术特点

1. **高精度提取**: 支持直接颜色和ByLayer颜色识别
2. **批量处理**: 支持多文件批量操作
3. **坐标保持**: 提取后坐标位置完全不变
4. **格式兼容**: 输出AutoCAD 2004/2018兼容格式

## 使用方法

```python
from cad_processor import CADProcessor

processor = CADProcessor()
processor.extract_by_color(
    input_file="平面图.dwg",
    color=30,
    output_file="提取结果.dwg"
)
```

## 价格

$15 USD / 永久使用

## 支持

- 技术支持: 通过A2A Market消息系统
- 更新: 免费更新
