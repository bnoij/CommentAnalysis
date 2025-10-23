<!-- @format -->

# 购物平台评论情感分析系统

基于 Python + SnowNLP + Ionic 的购物评论情感分析系统,支持多分类、多特征工程和模型集成。

## 项目特性

### 1. 多分类情感分析

-   将评论分为**正面**、**中性**、**负面**三类
-   提供每个类别的概率评分
-   基于 SnowNLP 扩展实现

### 2. 特征工程优化

支持多种特征提取方法,用户可自由选择:

-   **基础词袋特征**: 词频统计、字符统计等
-   **N-gram 特征**: 二元组、三元组特征
-   **字符级特征**: 字符 n-gram、标点符号统计
-   **情感词典特征**: 基于预定义情感词典的特征
-   **TF-IDF 特征**: 词频-逆文档频率特征

### 3. 模型集成

-   **投票集成**: 多个模型投票决定最终结果
-   **堆叠集成**: 基于权重的模型融合
-   结合不同阈值的模型提升准确率

### 4. 多语言支持

-   **中文**: 基于 SnowNLP 和 jieba 分词
-   **英文**: 基于 TextBlob
-   一键切换分析语言

### 5. 可视化展示

-   情感分布饼图
-   平均概率柱状图
-   详细结果列表
-   导出 CSV 功能

## 技术栈

### 后端

-   **Python 3.8+**
-   **Flask**: Web 框架
-   **SnowNLP**: 中文情感分析
-   **TextBlob**: 英文情感分析
-   **jieba**: 中文分词
-   **pandas**: 数据处理

### 前端

-   **Ionic Framework**: 移动端 UI 框架
-   **Vue 3**: JavaScript 框架
-   **TypeScript**: 类型安全
-   **ECharts**: 数据可视化
-   **Axios**: HTTP 客户端

## 安装和运行

### 后端安装

1. 进入后端目录:

```bash
cd backend
```

2. 安装 Python 依赖:

```bash
pip install -r requirements.txt
```

3. 启动 Flask 服务:

```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动

### 前端安装

1. 返回项目根目录:

```bash
cd ..
```

2. 安装 Node.js 依赖:

```bash
npm install
```

3. 启动开发服务器:

```bash
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

## 使用说明

### 1. 准备 CSV 文件

CSV 文件必须包含以下列之一:

-   `comment`: 评论内容
-   `text`: 文本内容
-   `review`: 评论内容

示例文件见:

-   `backend/sample_comments.csv` (中文示例)
-   `backend/sample_comments_en.csv` (英文示例)

### 2. 配置分析参数

-   **选择语言**: 中文或英文
-   **选择特征**: 可多选特征工程方法
-   **模型集成**: 开启或关闭模型集成

### 3. 上传并分析

1. 点击"选择 CSV 文件"按钮上传文件
2. 配置分析参数
3. 点击"开始分析"按钮
4. 等待分析完成

### 4. 查看结果

-   查看统计信息(总数、各类别数量和占比)
-   查看可视化图表(饼图、柱状图)
-   浏览详细分析结果
-   导出结果为 CSV 文件

## 项目结构

```
snownlp/
├── backend/                    # Python后端
│   ├── app.py                 # Flask主程序
│   ├── sentiment_analyzer.py # 情感分析器
│   ├── feature_engineering.py# 特征工程
│   ├── models.py              # 模型定义
│   ├── requirements.txt       # Python依赖
│   ├── sample_comments.csv    # 中文示例数据
│   ├── sample_comments_en.csv # 英文示例数据
│   └── README.md              # 后端说明
├── src/                       # 前端源码
│   ├── views/
│   │   └── HomePage.vue       # 主页面
│   ├── router/
│   │   └── index.ts           # 路由配置
│   └── main.ts                # 入口文件
├── package.json               # Node.js依赖
└── README.md                  # 项目说明
```

## API 接口

### 1. 健康检查

```
GET /api/health
```

### 2. 获取配置选项

```
GET /api/config
```

### 3. 情感分析

```
POST /api/analyze
Content-Type: multipart/form-data

参数:
- file: CSV文件
- language: 语言 (zh/en)
- features[]: 特征列表
- use_ensemble: 是否使用集成 (true/false)
```

## 核心算法

### 多分类实现

使用 SnowNLP 的情感得分,结合阈值和特征调整:

-   score >= 0.6: 正面倾向
-   0.4 < score < 0.6: 中性倾向
-   score <= 0.4: 负面倾向

### 概率计算

基于情感得分和情感词典特征动态调整三分类概率。

### 模型集成

-   **投票集成**: 平均多个模型的概率预测
-   **堆叠集成**: 使用加权平均,根据特征进一步调整

## 注意事项

1. CSV 文件大小限制为 16MB
2. 确保 CSV 文件使用 UTF-8 编码
3. 后端服务需要先启动才能进行分析
4. 首次运行可能需要下载 jieba 词典
5. 英文分析需要安装 TextBlob 库

## 示例数据

项目提供了两个示例 CSV 文件:

-   `backend/sample_comments.csv`: 15 条中文评论
-   `backend/sample_comments_en.csv`: 15 条英文评论

可以直接使用这些文件测试系统功能。

## 扩展建议

1. **增加训练数据**: 使用更大规模的标注数据训练模型
2. **深度学习模型**: 集成 BERT、RoBERTa 等预训练模型
3. **实时分析**: 添加流式数据处理能力
4. **情感强度**: 增加情感强度评分(0-10 分)
5. **关键词提取**: 提取每个类别的关键词
6. **时间序列**: 分析情感随时间的变化趋势

## 常见问题

**Q: 为什么分析结果不准确?**
A: 可以尝试:

-   选择更多特征工程方法
-   开启模型集成
-   使用更大的训练数据集

**Q: 如何处理其他语言?**
A: 可以扩展 models.py,添加对应语言的情感分析库。

**Q: 能否分析实时评论?**
A: 当前版本支持批量分析,可以扩展为 WebSocket 实时推送。

## 许可证

MIT License

## 作者

情感分析系统开发团队

## 更新日志

### v1.0.0 (2025-10-23)

-   初始版本发布
-   支持中英文情感分析
-   实现多分类和特征工程
-   添加模型集成功能
-   完成 Ionic 前端界面
