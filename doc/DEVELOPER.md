<!-- @format -->

# 开发者指南

## 🎯 开发环境搭建

### 必需工具

-   Python 3.8+
-   Node.js 16+
-   Git
-   VS Code (推荐)

### 推荐插件 (VS Code)

-   Python
-   Pylance
-   Volar (Vue)
-   ESLint
-   Prettier

## 📦 项目初始化

### 1. 克隆项目

```bash
git clone <repository-url>
cd snownlp
```

### 2. 后端开发环境

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest black flake8 mypy
```

### 3. 前端开发环境

```bash
cd ..

# 安装依赖
npm install

# 安装开发工具
npm install -D @types/node
```

## 🏗️ 代码结构说明

### 后端架构

```python
backend/
├── app.py                    # Flask应用入口
├── config.py                 # 配置管理
├── sentiment_analyzer.py     # 核心分析器
│   └── SentimentAnalyzer    # 主类
│       ├── analyze_single()  # 单条分析
│       ├── analyze_batch()   # 批量分析
│       └── get_statistics()  # 统计计算
│
├── feature_engineering.py    # 特征工程
│   └── FeatureExtractor      # 特征提取器
│       ├── extract_basic()
│       ├── extract_ngram()
│       ├── extract_char()
│       ├── extract_sentiment_dict()
│       └── extract_tfidf()
│
└── models.py                 # 模型定义
    ├── MultiClassSentiment   # 多分类模型
    └── EnsembleModel         # 集成模型
```

### 前端架构

```typescript
src/
├── main.ts                   # 应用入口
├── App.vue                   # 根组件
├── router/
│   └── index.ts             # 路由配置
└── views/
    └── HomePage.vue         # 主页面
        ├── 数据定义
        ├── 配置管理
        ├── 文件处理
        ├── API调用
        └── 图表渲染
```

## 🔧 核心模块详解

### 1. 情感分析器 (sentiment_analyzer.py)

#### 工作流程

```
文本输入 → 预处理 → 特征提取 → 模型预测 → 概率计算 → 结果输出
```

#### 关键方法

**preprocess_text(text)**

```python
def preprocess_text(self, text: str) -> str:
    """
    文本预处理
    - 移除特殊字符
    - 标准化空格
    - 保留关键标点
    """
    # 实现...
```

**analyze_single(text)**

```python
def analyze_single(self, text: str) -> Dict[str, Any]:
    """
    分析单条评论
    返回: {
        'text': 原文,
        'sentiment': 分类,
        'probabilities': 概率字典,
        'score': 综合得分
    }
    """
    # 实现...
```

### 2. 特征工程 (feature_engineering.py)

#### 特征类型

**基础特征**

```python
{
    'word_count': 词数,
    'char_count': 字符数,
    'avg_word_length': 平均词长,
    'unique_words': 唯一词数
}
```

**N-gram 特征**

```python
{
    'bigram_count': 二元组数量,
    'trigram_count': 三元组数量,
    'top_bigrams': 高频二元组,
    'top_trigrams': 高频三元组
}
```

**情感词典特征**

```python
{
    'positive_words': 正面词数,
    'negative_words': 负面词数,
    'sentiment_score': 情感得分,
    'sentiment_ratio': 情感比例
}
```

#### 扩展情感词典

编辑 `_load_sentiment_dict()` 方法:

```python
def _load_sentiment_dict(self):
    zh_dict = {
        # 添加领域相关词汇
        '性价比': 1,
        '物美价廉': 1,
        '虚假宣传': -1,
        # ...
    }
    return zh_dict
```

### 3. 模型模块 (models.py)

#### MultiClassSentiment

**阈值配置**

```python
class MultiClassSentiment:
    def __init__(self):
        self.positive_threshold = 0.6  # 可调
        self.negative_threshold = 0.4  # 可调
```

**概率计算逻辑**

```python
if score >= positive_threshold:
    # 正面倾向计算
elif score <= negative_threshold:
    # 负面倾向计算
else:
    # 中性倾向计算
```

#### EnsembleModel

**投票集成**

```python
def _voting_ensemble(self, predictions):
    # 平均所有模型的概率
    avg_probs = {
        'positive': mean([p['positive'] for _, p in predictions]),
        'neutral': mean([p['neutral'] for _, p in predictions]),
        'negative': mean([p['negative'] for _, p in predictions])
    }
    return determine_sentiment(avg_probs)
```

**堆叠集成**

```python
def _stacking_ensemble(self, predictions, features):
    weights = [0.4, 0.3, 0.3]  # 可调

    # 加权平均
    weighted = sum(w * p for w, p in zip(weights, predictions))

    # 基于特征调整
    if features['sentiment_score'] > 2:
        weighted['positive'] *= 1.15

    return weighted
```

## 🎨 前端开发

### 组件结构

**HomePage.vue** 分为以下部分:

1. **配置面板**: 参数选择
2. **进度显示**: 分析状态
3. **统计卡片**: 结果概览
4. **图表展示**: 可视化
5. **详细列表**: 完整结果

### 状态管理

```typescript
// 核心状态
const selectedFile = ref<File | null>(null);
const analyzing = ref(false);
const results = ref<any>(null);

// 配置状态
const config = ref({
    language: "zh",
    features: ["basic", "sentiment_dict"],
    useEnsemble: false,
});
```

### API 调用

```typescript
const analyzeComments = async () => {
    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append(
        "language",
        config.value.language
    );

    const response = await axios.post(
        "/api/analyze",
        formData
    );
    results.value = response.data;
};
```

### 图表渲染

```typescript
const renderCharts = () => {
    // 饼图
    const pie = echarts.init(pieChart.value);
    pie.setOption({
        series: [
            {
                type: "pie",
                data: [
                    {
                        value: stats.positive,
                        name: "正面",
                    },
                    {
                        value: stats.neutral,
                        name: "中性",
                    },
                    {
                        value: stats.negative,
                        name: "负面",
                    },
                ],
            },
        ],
    });

    // 柱状图
    // ...
};
```

## 🧪 测试

### 后端测试

**运行测试脚本**

```bash
cd backend
python test.py
```

**单元测试框架**

```python
import pytest

def test_sentiment_analysis():
    analyzer = SentimentAnalyzer(language='zh')
    result = analyzer.analyze_single("这个商品很好")
    assert result['sentiment'] == 'positive'
    assert result['probabilities']['positive'] > 0.6

def test_feature_extraction():
    extractor = FeatureExtractor(language='zh')
    features = extractor.extract("测试文本")
    assert 'basic' in features
```

### 前端测试

**E2E 测试**

```bash
npm run test:e2e
```

**单元测试**

```bash
npm run test:unit
```

## 📝 代码规范

### Python 代码规范

**使用 Black 格式化**

```bash
black backend/*.py
```

**Flake8 检查**

```bash
flake8 backend --max-line-length=100
```

**类型检查**

```bash
mypy backend
```

### TypeScript 代码规范

**ESLint 检查**

```bash
npm run lint
```

**Prettier 格式化**

```bash
npx prettier --write "src/**/*.{ts,vue}"
```

## 🔄 Git 工作流

### 分支策略

-   `main`: 生产环境
-   `develop`: 开发环境
-   `feature/*`: 功能分支
-   `bugfix/*`: 修复分支

### Commit 规范

```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建工具或辅助工具的变动
```

示例:

```bash
git commit -m "feat: 添加情感强度评分功能"
git commit -m "fix: 修复中文分词错误"
```

## 🚀 新功能开发流程

### 1. 添加新特征

**步骤**:

1. 在 `feature_engineering.py` 添加提取方法
2. 在 `FeatureExtractor.extract()` 中注册
3. 在前端添加选项
4. 测试验证

**示例**: 添加词性特征

```python
def extract_pos_features(self, text: str):
    """提取词性特征"""
    import jieba.posseg as pseg

    words = pseg.cut(text)
    pos_count = {}
    for word, pos in words:
        pos_count[pos] = pos_count.get(pos, 0) + 1

    return {
        'noun_count': pos_count.get('n', 0),
        'verb_count': pos_count.get('v', 0),
        'adj_count': pos_count.get('a', 0)
    }
```

### 2. 添加新模型

**步骤**:

1. 在 `models.py` 创建新类
2. 实现 `predict()` 方法
3. 在集成模型中注册
4. 调整权重

**示例**: 添加 SVM 模型

```python
class SVMSentiment:
    def __init__(self):
        from sklearn.svm import SVC
        self.model = SVC(probability=True)

    def predict(self, text, features):
        # 特征向量化
        X = vectorize(features)
        # 预测
        probs = self.model.predict_proba(X)
        return sentiment, probs
```

### 3. 添加新语言

**步骤**:

1. 添加该语言的情感分析库
2. 在 `models.py` 添加支持
3. 在 `feature_engineering.py` 添加分词
4. 更新前端选项

## 🐛 调试技巧

### 后端调试

**启用 Flask 调试模式**

```python
app.run(debug=True)
```

**添加日志**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
app.logger.debug('调试信息')
```

**使用 pdb 调试器**

```python
import pdb
pdb.set_trace()  # 设置断点
```

### 前端调试

**浏览器开发者工具**

-   Network: 查看 API 请求
-   Console: 查看日志和错误
-   Vue DevTools: 查看组件状态

**添加日志**

```typescript
console.log("调试信息:", variable);
console.error("错误:", error);
```

## 📊 性能优化

### 后端优化

**1. 使用缓存**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_text(text):
    # 缓存分析结果
```

**2. 批量处理**

```python
def analyze_batch_optimized(texts):
    # 向量化处理
    features = [extract(t) for t in texts]
    results = model.predict_batch(features)
    return results
```

**3. 异步处理**

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(analyze_single, texts)
```

### 前端优化

**1. 虚拟滚动**

```typescript
// 对于大量结果使用虚拟滚动
import { IonVirtualScroll } from "@ionic/vue";
```

**2. 懒加载图表**

```typescript
// 延迟渲染图表
setTimeout(() => renderCharts(), 100);
```

**3. 防抖处理**

```typescript
import { debounce } from "lodash";

const debouncedAnalyze = debounce(
    analyzeComments,
    500
);
```

## 📚 扩展资源

### 学习资源

-   [SnowNLP 文档](https://github.com/isnowfy/snownlp)
-   [Flask 文档](https://flask.palletsprojects.com/)
-   [Ionic Vue 文档](https://ionicframework.com/docs/vue/overview)
-   [ECharts 文档](https://echarts.apache.org/)

### 相关项目

-   TextBlob
-   NLTK
-   spaCy
-   Transformers (Hugging Face)

## 🤝 贡献代码

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 推送到分支
5. 创建 Pull Request

## 📧 联系方式

-   GitHub: [项目地址]
-   Email: dev@example.com
-   讨论组: [链接]

---

**Happy Coding! 🎉**
