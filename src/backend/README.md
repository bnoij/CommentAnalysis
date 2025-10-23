<!-- @format -->

# 购物平台评论情感分析系统 - 后端

## 功能特性

1. **多分类情感分析**: 将评论分为正面、中性、负面三类,并给出每个类别的概率
2. **多种特征工程方法**:
    - 基础词袋特征
    - N-gram 特征
    - 字符级特征
    - 情感词典特征
    - TF-IDF 特征
3. **模型集成**: 支持投票和堆叠两种集成方法
4. **多语言支持**: 支持中文和英文情感分析

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

## API 端点

### 1. 健康检查

-   **URL**: `/api/health`
-   **方法**: GET
-   **响应**: `{"status": "healthy", "message": "情感分析服务运行正常"}`

### 2. 获取配置

-   **URL**: `/api/config`
-   **方法**: GET
-   **响应**: 返回可用的语言、特征和集成方法选项

### 3. 情感分析

-   **URL**: `/api/analyze`
-   **方法**: POST
-   **参数**:
    -   `file`: CSV 文件(必须包含 comment/text/review 列)
    -   `language`: 语言选择(zh/en)
    -   `features[]`: 特征工程方法列表
    -   `use_ensemble`: 是否使用模型集成(true/false)
-   **响应**: 返回分析结果和统计信息

## CSV 文件格式

CSV 文件必须包含以下列之一:

-   `comment`: 评论内容
-   `text`: 文本内容
-   `review`: 评论内容

示例:

```csv
comment
这个商品质量很好,非常满意!
物流太慢了,包装也不好
还可以,价格合适
```

## 项目结构

```
backend/
├── app.py                    # Flask API服务
├── sentiment_analyzer.py     # 情感分析器核心
├── feature_engineering.py    # 特征工程模块
├── models.py                 # 模型定义
├── requirements.txt          # 依赖包
└── README.md                # 说明文档
```
