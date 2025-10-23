"""
模型模块
实现多分类情感分析和模型集成
"""
import numpy as np
from typing import Tuple, Dict, Any
from snownlp import SnowNLP
try:
    from textblob import TextBlob
except:
    TextBlob = None

class MultiClassSentiment:
    """多分类情感分析模型"""
    
    def __init__(self, language='zh'):
        """
        初始化模型
        
        Args:
            language: 语言类型
        """
        self.language = language
        # 阈值设置
        self.positive_threshold = 0.6
        self.negative_threshold = 0.4
    
    def _get_snownlp_score(self, text: str) -> float:
        """使用SnowNLP获取情感得分"""
        try:
            s = SnowNLP(text)
            return s.sentiments
        except:
            return 0.5
    
    def _get_textblob_score(self, text: str) -> float:
        """使用TextBlob获取情感得分(英文)"""
        if TextBlob is None:
            return 0.5
        try:
            blob = TextBlob(text)
            # TextBlob返回[-1, 1],转换为[0, 1]
            polarity = blob.sentiment.polarity
            return (polarity + 1) / 2
        except:
            return 0.5
    
    def _calculate_probabilities(self, score: float, features: Dict[str, Any]) -> Dict[str, float]:
        """
        计算三分类概率
        
        使用情感得分和特征信息计算正面、中性、负面的概率
        """
        # 基础概率基于情感得分
        if score >= self.positive_threshold:
            # 正面倾向
            positive = score
            negative = 1 - score
            neutral = 1 - abs(2 * score - 1)
        elif score <= self.negative_threshold:
            # 负面倾向
            positive = score
            negative = 1 - score
            neutral = 1 - abs(2 * score - 1)
        else:
            # 中性倾向
            neutral = 1 - abs(2 * score - 1) * 2
            positive = score
            negative = 1 - score
        
        # 使用情感词典特征调整
        if 'sentiment_dict' in features:
            sent_features = features['sentiment_dict']
            pos_words = sent_features.get('positive_words', 0)
            neg_words = sent_features.get('negative_words', 0)
            
            # 根据情感词数量调整概率
            if pos_words > neg_words:
                positive *= 1.1
                negative *= 0.9
            elif neg_words > pos_words:
                negative *= 1.1
                positive *= 0.9
            else:
                neutral *= 1.1
        
        # 归一化
        total = positive + neutral + negative
        if total > 0:
            positive /= total
            neutral /= total
            negative /= total
        
        return {
            'positive': round(positive, 4),
            'neutral': round(neutral, 4),
            'negative': round(negative, 4)
        }
    
    def predict(self, text: str, features: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        """
        预测情感类别和概率
        
        Args:
            text: 输入文本
            features: 提取的特征
            
        Returns:
            (sentiment, probabilities) 情感类别和各类别概率
        """
        # 获取基础情感得分
        if self.language == 'zh':
            score = self._get_snownlp_score(text)
        else:
            score = self._get_textblob_score(text)
        
        # 计算三分类概率
        probabilities = self._calculate_probabilities(score, features)
        
        # 确定最终类别
        max_prob = max(probabilities.values())
        if probabilities['positive'] == max_prob:
            sentiment = 'positive'
        elif probabilities['negative'] == max_prob:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, probabilities


class EnsembleModel:
    """集成模型"""
    
    def __init__(self, language='zh', method='voting'):
        """
        初始化集成模型
        
        Args:
            language: 语言类型
            method: 集成方法 ('voting' 或 'stacking')
        """
        self.language = language
        self.method = method
        
        # 初始化多个基础模型
        self.models = [
            MultiClassSentiment(language=language),
        ]
        
        # 不同阈值的模型
        self.model_strict = MultiClassSentiment(language=language)
        self.model_strict.positive_threshold = 0.7
        self.model_strict.negative_threshold = 0.3
        
        self.model_loose = MultiClassSentiment(language=language)
        self.model_loose.positive_threshold = 0.55
        self.model_loose.negative_threshold = 0.45
        
        self.models.extend([self.model_strict, self.model_loose])
    
    def _voting_ensemble(self, predictions: list) -> Tuple[str, Dict[str, float]]:
        """投票集成"""
        # 收集所有概率
        all_probs = {
            'positive': [],
            'neutral': [],
            'negative': []
        }
        
        for _, probs in predictions:
            for key in all_probs:
                all_probs[key].append(probs[key])
        
        # 计算平均概率
        avg_probs = {
            key: round(np.mean(values), 4)
            for key, values in all_probs.items()
        }
        
        # 确定最终类别
        max_prob = max(avg_probs.values())
        if avg_probs['positive'] == max_prob:
            sentiment = 'positive'
        elif avg_probs['negative'] == max_prob:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, avg_probs
    
    def _stacking_ensemble(self, predictions: list, features: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        """堆叠集成"""
        # 使用特征加权
        weights = [0.4, 0.3, 0.3]  # 不同模型的权重
        
        # 加权平均
        weighted_probs = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        for i, (_, probs) in enumerate(predictions):
            for key in weighted_probs:
                weighted_probs[key] += probs[key] * weights[i]
        
        # 如果有情感词典特征,进一步调整
        if 'sentiment_dict' in features:
            sent_features = features['sentiment_dict']
            sent_score = sent_features.get('sentiment_score', 0)
            
            if sent_score > 2:
                weighted_probs['positive'] *= 1.15
            elif sent_score < -2:
                weighted_probs['negative'] *= 1.15
            else:
                weighted_probs['neutral'] *= 1.1
        
        # 归一化
        total = sum(weighted_probs.values())
        if total > 0:
            weighted_probs = {k: round(v/total, 4) for k, v in weighted_probs.items()}
        
        # 确定最终类别
        max_prob = max(weighted_probs.values())
        if weighted_probs['positive'] == max_prob:
            sentiment = 'positive'
        elif weighted_probs['negative'] == max_prob:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, weighted_probs
    
    def predict(self, text: str, features: Dict[str, Any]) -> Tuple[str, Dict[str, float]]:
        """
        集成预测
        
        Args:
            text: 输入文本
            features: 提取的特征
            
        Returns:
            (sentiment, probabilities) 情感类别和各类别概率
        """
        # 获取所有模型的预测
        predictions = []
        for model in self.models:
            pred = model.predict(text, features)
            predictions.append(pred)
        
        # 根据集成方法合并结果
        if self.method == 'voting':
            return self._voting_ensemble(predictions)
        else:  # stacking
            return self._stacking_ensemble(predictions, features)
