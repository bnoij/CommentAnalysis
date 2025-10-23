"""
情感分析器核心模块
支持多分类、多特征工程和模型集成
"""
import numpy as np
from typing import List, Dict, Any
from snownlp import SnowNLP
from feature_engineering import FeatureExtractor
from models import MultiClassSentiment, EnsembleModel
import re

class SentimentAnalyzer:
    """情感分析器主类"""
    
    def __init__(self, language='zh', features=None, use_ensemble=False):
        """
        初始化情感分析器
        
        Args:
            language: 语言类型 ('zh' 或 'en')
            features: 特征工程方法列表
            use_ensemble: 是否使用模型集成
        """
        self.language = language
        self.features = features or ['basic']
        self.use_ensemble = use_ensemble
        
        # 初始化特征提取器
        self.feature_extractor = FeatureExtractor(language=language, features=self.features)
        
        # 初始化模型
        if use_ensemble:
            self.model = EnsembleModel(language=language)
        else:
            self.model = MultiClassSentiment(language=language)
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        if not text or not isinstance(text, str):
            return ""
        
        # 移除特殊字符(保留中文、英文、数字和基本标点)
        if self.language == 'zh':
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,。!?、;:""''()【】《》\s]', '', text)
        else:
            text = re.sub(r'[^a-zA-Z0-9,.\s!?\'"()-]', '', text)
        
        # 移除多余空格
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_single(self, text: str) -> Dict[str, Any]:
        """
        分析单条评论
        
        Args:
            text: 评论文本
            
        Returns:
            包含情感分析结果的字典
        """
        # 预处理
        clean_text = self.preprocess_text(text)
        
        if not clean_text:
            return {
                'text': text,
                'sentiment': 'neutral',
                'probabilities': {
                    'positive': 0.33,
                    'neutral': 0.34,
                    'negative': 0.33
                },
                'score': 0.5
            }
        
        # 提取特征
        features = self.feature_extractor.extract(clean_text)
        
        # 获取预测结果
        sentiment, probabilities = self.model.predict(clean_text, features)
        
        # 计算综合得分(正面概率)
        score = probabilities['positive']
        
        return {
            'text': text,
            'sentiment': sentiment,
            'probabilities': probabilities,
            'score': round(score, 4)
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        批量分析评论
        
        Args:
            texts: 评论文本列表
            
        Returns:
            分析结果列表
        """
        results = []
        for text in texts:
            result = self.analyze_single(text)
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算统计信息
        
        Args:
            results: 分析结果列表
            
        Returns:
            统计信息字典
        """
        total = len(results)
        if total == 0:
            return {}
        
        # 统计各类别数量
        positive_count = sum(1 for r in results if r['sentiment'] == 'positive')
        neutral_count = sum(1 for r in results if r['sentiment'] == 'neutral')
        negative_count = sum(1 for r in results if r['sentiment'] == 'negative')
        
        # 计算平均概率
        avg_positive = np.mean([r['probabilities']['positive'] for r in results])
        avg_neutral = np.mean([r['probabilities']['neutral'] for r in results])
        avg_negative = np.mean([r['probabilities']['negative'] for r in results])
        
        # 计算平均得分
        avg_score = np.mean([r['score'] for r in results])
        
        return {
            'total': total,
            'counts': {
                'positive': positive_count,
                'neutral': neutral_count,
                'negative': negative_count
            },
            'percentages': {
                'positive': round(positive_count / total * 100, 2),
                'neutral': round(neutral_count / total * 100, 2),
                'negative': round(negative_count / total * 100, 2)
            },
            'average_probabilities': {
                'positive': round(avg_positive, 4),
                'neutral': round(avg_neutral, 4),
                'negative': round(avg_negative, 4)
            },
            'average_score': round(avg_score, 4)
        }
