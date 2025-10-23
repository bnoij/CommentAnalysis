"""
购物平台评论情感分析系统 - Flask API服务
支持中英文情感分析、多种特征工程方法和模型集成
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename
from sentiment_analyzer import SentimentAnalyzer
from config import config

# 创建Flask应用
app = Flask(__name__)

# 加载配置
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# 配置CORS
CORS(app, resources={
    r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "X-Requested-With"]
    }
})

# 开发环境额外添加通配符支持
if app.config['DEBUG']:
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin and origin.startswith('http://localhost'):
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def _calculate_time_statistics(results, df, date_col):
    """计算时间维度的情感统计"""
    try:
        # 解析日期
        dates = pd.to_datetime(df[date_col], errors='coerce')
        
        # 创建包含日期和情感的DataFrame
        time_df = pd.DataFrame({
            'date': dates,
            'sentiment': [r['sentiment'] for r in results],
            'positive_prob': [r['probabilities']['positive'] for r in results],
            'neutral_prob': [r['probabilities']['neutral'] for r in results],
            'negative_prob': [r['probabilities']['negative'] for r in results]
        })
        
        # 移除无效日期
        time_df = time_df.dropna(subset=['date'])
        
        if len(time_df) == 0:
            return None
        
        # 按日期分组统计
        time_df['date_str'] = time_df['date'].dt.strftime('%Y-%m-%d')
        daily_stats = time_df.groupby('date_str').agg({
            'sentiment': lambda x: {
                'positive': (x == 'positive').sum(),
                'neutral': (x == 'neutral').sum(),
                'negative': (x == 'negative').sum()
            },
            'positive_prob': 'mean',
            'neutral_prob': 'mean',
            'negative_prob': 'mean'
        }).to_dict()
        
        # 按月份统计
        time_df['month'] = time_df['date'].dt.strftime('%Y-%m')
        monthly_stats = time_df.groupby('month').agg({
            'sentiment': lambda x: {
                'positive': (x == 'positive').sum(),
                'neutral': (x == 'neutral').sum(),
                'negative': (x == 'negative').sum(),
                'total': len(x)
            }
        }).to_dict()
        
        # 构建返回数据
        dates_list = sorted(time_df['date_str'].unique())
        sentiment_by_date = {}
        avg_prob_by_date = {}
        
        for date in dates_list:
            date_data = time_df[time_df['date_str'] == date]
            sentiment_by_date[date] = {
                'positive': int((date_data['sentiment'] == 'positive').sum()),
                'neutral': int((date_data['sentiment'] == 'neutral').sum()),
                'negative': int((date_data['sentiment'] == 'negative').sum())
            }
            avg_prob_by_date[date] = {
                'positive': float(date_data['positive_prob'].mean()),
                'neutral': float(date_data['neutral_prob'].mean()),
                'negative': float(date_data['negative_prob'].mean())
            }
        
        return {
            'dates': dates_list,
            'sentiment_by_date': sentiment_by_date,
            'avg_prob_by_date': avg_prob_by_date,
            'date_range': {
                'start': time_df['date'].min().strftime('%Y-%m-%d'),
                'end': time_df['date'].max().strftime('%Y-%m-%d')
            }
        }
    except Exception as e:
        print(f"时间统计错误: {e}")
        return None

def _calculate_location_statistics(results, df, location_col):
    """计算地域维度的情感统计"""
    try:
        # 创建包含地域和情感的DataFrame
        location_df = pd.DataFrame({
            'location': df[location_col].fillna('未知'),
            'sentiment': [r['sentiment'] for r in results],
            'positive_prob': [r['probabilities']['positive'] for r in results],
            'neutral_prob': [r['probabilities']['neutral'] for r in results],
            'negative_prob': [r['probabilities']['negative'] for r in results]
        })
        
        # 按地域分组统计
        location_stats = location_df.groupby('location').agg({
            'sentiment': lambda x: {
                'positive': int((x == 'positive').sum()),
                'neutral': int((x == 'neutral').sum()),
                'negative': int((x == 'negative').sum()),
                'total': int(len(x))
            },
            'positive_prob': 'mean',
            'neutral_prob': 'mean',
            'negative_prob': 'mean'
        })
        
        # 构建返回数据
        locations = []
        sentiment_counts = []
        avg_probs = []
        
        for location in location_stats.index:
            if location and location != '未知':
                sentiment_data = location_stats.loc[location, 'sentiment']
                locations.append(location)
                sentiment_counts.append({
                    'location': location,
                    'positive': sentiment_data['positive'],
                    'neutral': sentiment_data['neutral'],
                    'negative': sentiment_data['negative'],
                    'total': sentiment_data['total']
                })
                avg_probs.append({
                    'location': location,
                    'positive': float(location_stats.loc[location, 'positive_prob']),
                    'neutral': float(location_stats.loc[location, 'neutral_prob']),
                    'negative': float(location_stats.loc[location, 'negative_prob'])
                })
        
        # 按总数排序，取前20个地区
        sentiment_counts.sort(key=lambda x: x['total'], reverse=True)
        top_locations = sentiment_counts[:20]
        
        return {
            'locations': [item['location'] for item in top_locations],
            'sentiment_by_location': {item['location']: {
                'positive': item['positive'],
                'neutral': item['neutral'],
                'negative': item['negative']
            } for item in top_locations},
            'avg_prob_by_location': {item['location']: {
                'positive': next((p['positive'] for p in avg_probs if p['location'] == item['location']), 0),
                'neutral': next((p['neutral'] for p in avg_probs if p['location'] == item['location']), 0),
                'negative': next((p['negative'] for p in avg_probs if p['location'] == item['location']), 0)
            } for item in top_locations},
            'total_locations': len(locations)
        }
    except Exception as e:
        print(f"地域统计错误: {e}")
        return None

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    """
    情感分析API端点
    接收CSV文件和分析参数,返回情感分析结果
    """
    try:
        # 检查文件是否上传
        if 'file' not in request.files:
            return jsonify({'error': '未上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '只支持CSV文件'}), 400
        
        # 获取分析参数
        language = request.form.get('language', 'zh')  # zh或en
        features = request.form.getlist('features[]')  # 特征工程方法列表
        use_ensemble = request.form.get('use_ensemble', 'false') == 'true'
        
        # 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 读取CSV文件
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # 检查CSV格式 - 支持多种列名
        possible_comment_cols = ['评论内容', 'comment', 'text', 'review', '评论']
        comment_col = None
        for col in possible_comment_cols:
            if col in df.columns:
                comment_col = col
                break
        
        if comment_col is None:
            return jsonify({'error': 'CSV文件必须包含评论内容、comment、text或review列'}), 400
        
        # 提取评论和元数据
        comments = df[comment_col].fillna('').astype(str).tolist()
        
        # 提取日期和地域信息（如果存在）
        date_col = None
        location_col = None
        
        for col in ['评论日期', 'date', '日期']:
            if col in df.columns:
                date_col = col
                break
        
        for col in ['购买地', 'location', '地域', '地区']:
            if col in df.columns:
                location_col = col
                break
        
        # 收集CSV文件统计信息
        file_stats = {
            'filename': file.filename,
            'total_rows': len(df),
            'columns': df.columns.tolist(),
            'has_date': date_col is not None,
            'has_location': location_col is not None,
        }
        
        # 添加其他可用列的统计
        if '产品类别' in df.columns:
            file_stats['product_categories'] = df['产品类别'].value_counts().head(10).to_dict()
        if '店铺' in df.columns:
            file_stats['top_shops'] = df['店铺'].value_counts().head(5).to_dict()
        if '价格' in df.columns:
            prices = pd.to_numeric(df['价格'], errors='coerce')
            file_stats['price_stats'] = {
                'min': float(prices.min()) if not prices.isna().all() else 0,
                'max': float(prices.max()) if not prices.isna().all() else 0,
                'avg': float(prices.mean()) if not prices.isna().all() else 0
            }
        
        # 创建情感分析器
        analyzer = SentimentAnalyzer(
            language=language,
            features=features if features else ['basic'],
            use_ensemble=use_ensemble
        )
        
        # 执行情感分析
        results = analyzer.analyze_batch(comments)
        
        # 为每个结果添加日期和地域信息
        for i, result in enumerate(results):
            if date_col and i < len(df):
                result['date'] = str(df.iloc[i][date_col]) if pd.notna(df.iloc[i][date_col]) else None
            if location_col and i < len(df):
                result['location'] = str(df.iloc[i][location_col]) if pd.notna(df.iloc[i][location_col]) else None
        
        # 计算时间和地域统计
        time_stats = None
        location_stats = None
        
        if date_col:
            time_stats = _calculate_time_statistics(results, df, date_col)
        
        if location_col:
            location_stats = _calculate_location_statistics(results, df, location_col)
        
        # 清理上传的文件
        os.remove(filepath)
        
        # 返回分析结果
        return jsonify({
            'success': True,
            'total': len(results),
            'results': results,
            'statistics': analyzer.get_statistics(results),
            'file_stats': file_stats,
            'time_stats': time_stats,
            'location_stats': location_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'message': '情感分析服务运行正常'})

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取可用的配置选项"""
    return jsonify({
        'languages': [
            {'value': 'zh', 'label': '中文'},
            {'value': 'en', 'label': '英文'}
        ],
        'features': [
            {'value': 'basic', 'label': '基础词袋特征'},
            {'value': 'ngram', 'label': 'N-gram特征'},
            {'value': 'char', 'label': '字符级特征'},
            {'value': 'sentiment_dict', 'label': '情感词典特征'},
            {'value': 'tfidf', 'label': 'TF-IDF特征'}
        ],
        'ensemble_methods': [
            {'value': 'voting', 'label': '投票集成'},
            {'value': 'stacking', 'label': '堆叠集成'}
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
