"""
测试脚本 - 验证后端功能
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentiment_analyzer import SentimentAnalyzer
import json

def test_chinese_analysis():
    """测试中文情感分析"""
    print("=" * 50)
    print("测试中文情感分析")
    print("=" * 50)
    
    # 创建分析器
    analyzer = SentimentAnalyzer(
        language='zh',
        features=['basic', 'sentiment_dict', 'ngram'],
        use_ensemble=False
    )
    
    # 测试评论
    comments = [
        "这个商品质量很好,非常满意!",
        "物流太慢了,包装也不好",
        "还可以,价格合适",
        "超级棒的购物体验,下次还会再来"
    ]
    
    # 分析
    results = analyzer.analyze_batch(comments)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"\n评论 {i}: {result['text']}")
        print(f"情感: {result['sentiment']}")
        print(f"概率分布:")
        print(f"  正面: {result['probabilities']['positive']:.4f}")
        print(f"  中性: {result['probabilities']['neutral']:.4f}")
        print(f"  负面: {result['probabilities']['negative']:.4f}")
    
    # 打印统计
    stats = analyzer.get_statistics(results)
    print(f"\n统计信息:")
    print(f"总数: {stats['total']}")
    print(f"正面: {stats['counts']['positive']} ({stats['percentages']['positive']}%)")
    print(f"中性: {stats['counts']['neutral']} ({stats['percentages']['neutral']}%)")
    print(f"负面: {stats['counts']['negative']} ({stats['percentages']['negative']}%)")

def test_english_analysis():
    """测试英文情感分析"""
    print("\n" + "=" * 50)
    print("测试英文情感分析")
    print("=" * 50)
    
    # 创建分析器
    analyzer = SentimentAnalyzer(
        language='en',
        features=['basic', 'sentiment_dict'],
        use_ensemble=False
    )
    
    # 测试评论
    comments = [
        "This product is amazing! Highly recommend it.",
        "Very disappointed with the quality.",
        "It's okay, nothing special.",
        "Great value for money!"
    ]
    
    # 分析
    results = analyzer.analyze_batch(comments)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"\n评论 {i}: {result['text']}")
        print(f"情感: {result['sentiment']}")
        print(f"概率分布:")
        print(f"  正面: {result['probabilities']['positive']:.4f}")
        print(f"  中性: {result['probabilities']['neutral']:.4f}")
        print(f"  负面: {result['probabilities']['negative']:.4f}")

def test_ensemble():
    """测试模型集成"""
    print("\n" + "=" * 50)
    print("测试模型集成")
    print("=" * 50)
    
    # 创建集成分析器
    analyzer = SentimentAnalyzer(
        language='zh',
        features=['basic', 'sentiment_dict', 'ngram', 'char'],
        use_ensemble=True
    )
    
    # 测试评论
    comments = [
        "这个商品质量很好,非常满意!",
        "太差了,完全不值这个价格"
    ]
    
    # 分析
    results = analyzer.analyze_batch(comments)
    
    # 打印结果
    for i, result in enumerate(results, 1):
        print(f"\n评论 {i}: {result['text']}")
        print(f"情感: {result['sentiment']}")
        print(f"概率分布:")
        print(f"  正面: {result['probabilities']['positive']:.4f}")
        print(f"  中性: {result['probabilities']['neutral']:.4f}")
        print(f"  负面: {result['probabilities']['negative']:.4f}")

def test_features():
    """测试不同特征组合"""
    print("\n" + "=" * 50)
    print("测试不同特征组合")
    print("=" * 50)
    
    text = "这个商品质量很好,非常满意!"
    
    feature_sets = [
        ['basic'],
        ['basic', 'sentiment_dict'],
        ['basic', 'ngram'],
        ['basic', 'sentiment_dict', 'ngram', 'char', 'tfidf']
    ]
    
    for features in feature_sets:
        print(f"\n使用特征: {', '.join(features)}")
        analyzer = SentimentAnalyzer(language='zh', features=features)
        result = analyzer.analyze_single(text)
        print(f"情感: {result['sentiment']}")
        print(f"正面概率: {result['probabilities']['positive']:.4f}")

if __name__ == '__main__':
    try:
        test_chinese_analysis()
        test_english_analysis()
        test_ensemble()
        test_features()
        
        print("\n" + "=" * 50)
        print("所有测试完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
