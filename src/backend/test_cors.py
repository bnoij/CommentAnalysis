"""
CORS配置测试脚本
用于验证CORS设置是否正确
"""
import requests
import sys

def test_cors():
    """测试CORS配置"""
    print("=" * 60)
    print("CORS配置测试")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    test_origins = [
        "http://localhost:5001",
        "http://localhost:5173",
        "http://localhost:8100"
    ]
    
    # 测试1: 健康检查
    print("\n[测试1] 健康检查端点...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 响应: {response.json()}")
    except Exception as e:
        print(f"✗ 错误: {e}")
        print("\n请确保后端服务正在运行: python backend/app.py")
        sys.exit(1)
    
    # 测试2: CORS预检请求
    print("\n[测试2] CORS预检请求...")
    for origin in test_origins:
        print(f"\n测试源: {origin}")
        try:
            response = requests.options(
                f"{base_url}/api/analyze",
                headers={
                    'Origin': origin,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'content-type'
                }
            )
            
            # 检查CORS头
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print(f"  ✓ Access-Control-Allow-Origin: {cors_header}")
            else:
                print(f"  ✗ 缺少 Access-Control-Allow-Origin 头")
            
            methods = response.headers.get('Access-Control-Allow-Methods')
            if methods:
                print(f"  ✓ Access-Control-Allow-Methods: {methods}")
            
            headers = response.headers.get('Access-Control-Allow-Headers')
            if headers:
                print(f"  ✓ Access-Control-Allow-Headers: {headers}")
                
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    # 测试3: 获取配置
    print("\n[测试3] 获取配置端点...")
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✓ 支持的语言: {len(config.get('languages', []))} 种")
            print(f"✓ 支持的特征: {len(config.get('features', []))} 种")
        else:
            print(f"✗ 状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 测试4: 模拟文件上传（使用测试数据）
    print("\n[测试4] 模拟分析请求...")
    try:
        # 创建测试CSV内容
        csv_content = "comment\n这个商品很好\n质量不错\n"
        files = {
            'file': ('test.csv', csv_content.encode('utf-8'), 'text/csv')
        }
        data = {
            'language': 'zh',
            'features[]': ['basic', 'sentiment_dict'],
            'use_ensemble': 'false'
        }
        
        response = requests.post(
            f"{base_url}/api/analyze",
            files=files,
            data=data,
            headers={'Origin': 'http://localhost:5001'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 分析成功")
            print(f"✓ 分析了 {result.get('total', 0)} 条评论")
            
            # 检查CORS头
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print(f"✓ CORS头存在: {cors_header}")
            else:
                print(f"✗ 响应中缺少CORS头")
        else:
            print(f"✗ 状态码: {response.status_code}")
            print(f"✗ 响应: {response.text}")
            
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print("\n如果看到 ✓ 标记，说明CORS配置正确")
    print("如果看到 ✗ 标记，请检查:")
    print("1. 后端服务是否正在运行")
    print("2. backend/config.py 中的 CORS_ORIGINS 配置")
    print("3. backend/app.py 中的 CORS 设置")

if __name__ == '__main__':
    try:
        test_cors()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()
