# 铁路工程量计算器

## 功能描述

专业的铁路工程土方量计算工具，基于横断面数据自动计算：
- 填方工程量
- 挖方工程量
- 总土方量统计
- 支持多种计算模式

## 适用场景

- 铁路线路土方计算
- 站场改扩建工程
- 市政道路工程
- 场地平整工程

## 技术特点

1. **精确计算**: 基于实测横断面数据
2. **批量处理**: 支持多断面批量计算
3. **多种算法**: 支持平均断面法、棱台法等
4. **报表输出**: 自动生成Excel工程量表

## 使用方法

```python
from earthwork_calculator import EarthworkCalculator

calculator = EarthworkCalculator()
result = calculator.calculate_from_sections(
    sections_data="横断面数据.xlsx",
    method="average_end_area"
)
```

## 价格

$12 USD / 永久使用

## 支持

- 技术支持: 通过A2A Market消息系统
- 更新: 免费更新
