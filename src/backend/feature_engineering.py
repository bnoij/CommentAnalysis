"""
特征工程模块
实现多种特征提取方法
"""
import jieba
import re
from typing import List, Dict, Any
from collections import Counter
import numpy as np

class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self, language='zh', features=None):
        """
        初始化特征提取器
        
        Args:
            language: 语言类型
            features: 要使用的特征列表
        """
        self.language = language
        self.features = features or ['basic']
        
        # 加载情感词典
        self.sentiment_dict = self._load_sentiment_dict()
    
    def _load_sentiment_dict(self) -> Dict[str, int]:
        """加载情感词典"""
        # 中文情感词典(简化版)
        zh_dict = {
            # 正面词
            '好': 1, '棒': 1, '优秀': 1, '满意': 1, '喜欢': 1, '推荐': 1,
            '值得': 1, '赞': 1, '完美': 1, '精致': 1, '舒适': 1, '实惠': 1,
            '快': 1, '方便': 1, '漂亮': 1, '美': 1, '不错': 1, '可以': 1,
            # 负面词
            '差': -1, '坏': -1, '烂': -1, '失望': -1, '不满': -1, '后悔': -1,
            '垃圾': -1, '骗': -1, '假': -1, '次': -1, '慢': -1, '贵': -1,
            '难用': -1, '不好': -1, '问题': -1, '糟糕': -1, '质量差': -1
        }
        
        # 英文情感词典(简化版)
        en_dict = {
            # Positive
            'good': 1, 'great': 1, 'excellent': 1, 'perfect': 1, 'love': 1,
            'like': 1, 'best': 1, 'amazing': 1, 'awesome': 1, 'wonderful': 1,
            'nice': 1, 'happy': 1, 'satisfied': 1, 'recommend': 1, 'worth': 1,
            # Negative
            'bad': -1, 'terrible': -1, 'poor': -1, 'worst': -1, 'hate': -1,
            'disappointing': -1, 'awful': -1, 'horrible': -1, 'waste': -1,
            'useless': -1, 'disappointed': -1, 'regret': -1, 'problem': -1
        }
        
        return zh_dict if self.language == 'zh' else en_dict
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        if self.language == 'zh':
            return list(jieba.cut(text))
        else:
            return text.lower().split()
    
    def extract_basic_features(self, text: str) -> Dict[str, Any]:
        """提取基础特征"""
        tokens = self._tokenize(text)
        
        return {
            'word_count': len(tokens),
            'char_count': len(text),
            'avg_word_length': np.mean([len(w) for w in tokens]) if tokens else 0,
            'unique_words': len(set(tokens))
        }
    
    def extract_ngram_features(self, text: str, n=2) -> Dict[str, Any]:
        """提取N-gram特征"""
        tokens = self._tokenize(text)
        
        # Bi-gram
        bigrams = [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
        bigram_freq = Counter(bigrams)
        
        # Tri-gram
        trigrams = [' '.join(tokens[i:i+3]) for i in range(len(tokens)-2)]
        trigram_freq = Counter(trigrams)
        
        return {
            'bigram_count': len(bigrams),
            'trigram_count': len(trigrams),
            'top_bigrams': bigram_freq.most_common(5),
            'top_trigrams': trigram_freq.most_common(3)
        }
    
    def extract_char_features(self, text: str) -> Dict[str, Any]:
        """提取字符级特征"""
        # 字符n-gram
        char_bigrams = [text[i:i+2] for i in range(len(text)-1)]
        char_trigrams = [text[i:i+3] for i in range(len(text)-2)]
        
        # 特殊字符统计
        exclamation_count = text.count('!') + text.count('!')
        question_count = text.count('?') + text.count('?')
        
        return {
            'char_bigram_count': len(set(char_bigrams)),
            'char_trigram_count': len(set(char_trigrams)),
            'exclamation_marks': exclamation_count,
            'question_marks': question_count,
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }
    
    def extract_sentiment_dict_features(self, text: str) -> Dict[str, Any]:
        """提取情感词典特征"""
        tokens = self._tokenize(text)
        
        positive_count = 0
        negative_count = 0
        sentiment_score = 0
        
        for token in tokens:
            if token in self.sentiment_dict:
                score = self.sentiment_dict[token]
                sentiment_score += score
                if score > 0:
                    positive_count += 1
                else:
                    negative_count += 1
        
        return {
            'positive_words': positive_count,
            'negative_words': negative_count,
            'sentiment_score': sentiment_score,
            'sentiment_ratio': (positive_count - negative_count) / len(tokens) if tokens else 0
        }
    
    def extract_tfidf_features(self, text: str) -> Dict[str, Any]:
        """提取TF-IDF特征(简化版)"""
        tokens = self._tokenize(text)
        token_freq = Counter(tokens)
        
        # 计算词频(TF)
        max_freq = max(token_freq.values()) if token_freq else 1
        tf_scores = {word: freq / max_freq for word, freq in token_freq.items()}
        
        # 获取高频词
        top_words = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'tf_features': dict(top_words),
            'max_tf': max(tf_scores.values()) if tf_scores else 0,
            'vocab_size': len(tf_scores)
        }
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        提取所有指定的特征
        
        Args:
            text: 输入文本
            
        Returns:
            特征字典
        """
        all_features = {}
        
        for feature_type in self.features:
            if feature_type == 'basic':
                all_features['basic'] = self.extract_basic_features(text)
            elif feature_type == 'ngram':
                all_features['ngram'] = self.extract_ngram_features(text)
            elif feature_type == 'char':
                all_features['char'] = self.extract_char_features(text)
            elif feature_type == 'sentiment_dict':
                all_features['sentiment_dict'] = self.extract_sentiment_dict_features(text)
            elif feature_type == 'tfidf':
                all_features['tfidf'] = self.extract_tfidf_features(text)
        
        return all_features
