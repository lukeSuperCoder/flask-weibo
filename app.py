from flask import Flask, jsonify, request
from flask_cors import CORS  # 用于处理跨域请求
from config import Config
from datetime import datetime, timedelta
from weibo_geom import weibo_geom_bp  # 导入微博地理信息蓝图
from models import db, WeiboGeom
from sqlalchemy import func, case

# 创建 Flask 应用实例
app = Flask(__name__)
CORS(app)  # 启用 CORS

# 加载配置
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 注册蓝图
app.register_blueprint(weibo_geom_bp)

# 示例模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# 微博数据模型
class Weibo(db.Model):
    __tablename__ = 'weibo'
    
    id = db.Column(db.String(20), primary_key=True)
    bid = db.Column(db.String(12), nullable=False)
    user_id = db.Column(db.String(20))
    screen_name = db.Column(db.String(30))
    text = db.Column(db.Text)
    article_url = db.Column(db.String(100))
    topics = db.Column(db.String(200))
    at_users = db.Column(db.String(1000))
    pics = db.Column(db.Text)
    video_url = db.Column(db.String(1000))
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)
    source = db.Column(db.String(30))
    attitudes_count = db.Column(db.Integer)
    comments_count = db.Column(db.Integer)
    reposts_count = db.Column(db.Integer)
    retweet_id = db.Column(db.String(20))
    ip = db.Column(db.String(100))
    user_authentication = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'bid': self.bid,
            'user_id': self.user_id,
            'screen_name': self.screen_name,
            'text': self.text,
            'article_url': self.article_url,
            'topics': self.topics,
            'at_users': self.at_users,
            'pics': self.pics,
            'video_url': self.video_url,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source': self.source,
            'attitudes_count': self.attitudes_count,
            'comments_count': self.comments_count,
            'reposts_count': self.reposts_count,
            'retweet_id': self.retweet_id,
            'ip': self.ip,
            'user_authentication': self.user_authentication
        }

# 创建数据库表
with app.app_context():
    db.create_all()

# 示例路由
@app.route('/api/hello', methods=['GET'])
def hello():
    """
    示例接口：返回欢迎信息
    """
    return jsonify({
        'code': 200,
        'message': '欢迎使用 Flask API 服务',
        'data': None
    })

# 微博 CRUD 接口
@app.route('/api/weibo', methods=['POST'])
def create_weibo():
    """创建微博"""
    data = request.get_json()
    try:
        # 转换日期字符串为 datetime 对象
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        weibo = Weibo(**data)
        db.session.add(weibo)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': weibo.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500

@app.route('/api/weibo/<id>', methods=['GET'])
def get_weibo(id):
    """获取单条微博"""
    weibo = Weibo.query.get(id)
    if weibo:
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': weibo.to_dict()
        })
    return jsonify({
        'code': 404,
        'message': '微博不存在',
        'data': None
    }), 404

@app.route('/api/weibo', methods=['GET'])
def get_weibo_list():
    """获取微博列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    query = Weibo.query
    # 添加筛选条件
    if 'id' in request.args:
        query = query.filter(Weibo.id == request.args['id'])
    if 'bid' in request.args:
        query = query.filter(Weibo.bid == request.args['bid'])
    if 'user_id' in request.args:
        query = query.filter(Weibo.user_id == request.args['user_id'])
    if 'screen_name' in request.args:
        query = query.filter(Weibo.screen_name.like(f"%{request.args['screen_name']}%"))
    
    # 按 created_at 时间从大到小排序
    pagination = query.order_by(Weibo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    # 格式化时间
    items = []
    for weibo in pagination.items:
        weibo_data = weibo.to_dict()
        if 'created_at' in weibo_data:
            weibo_data['created_at'] = weibo_data['created_at']  # 格式化时间为2025-04-12 00:32:00.000
        items.append(weibo_data)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })

@app.route('/api/weibo/<id>', methods=['PUT'])
def update_weibo(id):
    """更新微博"""
    weibo = Weibo.query.get(id)
    if not weibo:
        return jsonify({
            'code': 404,
            'message': '微博不存在',
            'data': None
        }), 404
    
    data = request.get_json()
    try:
        # 转换日期字符串为 datetime 对象
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        for key, value in data.items():
            setattr(weibo, key, value)
        
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': weibo.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500

@app.route('/api/weibo/<id>', methods=['DELETE'])
def delete_weibo(id):
    """删除微博"""
    weibo = Weibo.query.get(id)
    if not weibo:
        return jsonify({
            'code': 404,
            'message': '微博不存在',
            'data': None
        }), 404
    
    try:
        db.session.delete(weibo)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500

# 按时间统计微博数量
@app.route('/api/weibo/time_stats', methods=['GET'])
def get_weibo_time_stats():
    """获取按时间统计的微博数量"""
    # 获取开始和结束时间
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 如果没有指定时间范围，默认使用最近7天
    if not start_date or not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # 构建查询
    query = db.session.query(
        func.date(Weibo.created_at).label('date'),
        func.count(case((Weibo.attitudes_count > 1000, 1))).label('hot_count'),
        func.count(case((Weibo.attitudes_count <= 1000, 1))).label('normal_count')
    ).filter(
        func.date(Weibo.created_at) >= start_date,
        func.date(Weibo.created_at) <= end_date
    ).group_by(
        func.date(Weibo.created_at)
    ).order_by(
        func.date(Weibo.created_at)
    )
    
    # 执行查询
    results = query.all()
    
    # 处理结果
    date_list = []
    hot_count_list = []
    normal_count_list = []
    
    for result in results:
        date_list.append(result.date.strftime('%Y-%m-%d'))
        hot_count_list.append(result.hot_count)
        normal_count_list.append(result.normal_count)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'dateList': date_list,
            'numList': hot_count_list,  # 热点数据
            'numList2': normal_count_list  # 普通数据
        }
    })

# 关联查询接口
@app.route('/api/weibo/with_geom/<id>', methods=['GET'])
def get_weibo_with_geom(id):
    """获取微博及其地理信息"""
    # 查询微博信息
    weibo = Weibo.query.get(id)
    if not weibo:
        return jsonify({
            'code': 404,
            'message': '微博不存在',
            'data': None
        }), 404
    
    # 查询地理信息
    weibo_geom = WeiboGeom.query.get(id)
    
    # 合并数据
    result = weibo.to_dict()
    if weibo_geom:
        geom_data = weibo_geom.to_dict()
        # 添加地理信息
        result.update({
            'point': geom_data['point'],
            'geometry': geom_data['geometry']
        })
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': result
    })

# 批量关联查询接口
@app.route('/api/weibo/with_geom', methods=['GET'])
def get_weibo_list_with_geom():
    """获取微博列表及其地理信息"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    # 构建查询
    query = db.session.query(Weibo, WeiboGeom).outerjoin(
        WeiboGeom, Weibo.id == WeiboGeom.id
    )
    
    # 添加筛选条件
    if 'id' in request.args:
        query = query.filter(Weibo.id == request.args['id'])
    if 'bid' in request.args:
        query = query.filter(Weibo.bid == request.args['bid'])
    if 'user_id' in request.args:
        query = query.filter(Weibo.user_id == request.args['user_id'])
    if 'screen_name' in request.args:
        query = query.filter(Weibo.screen_name.like(f"%{request.args['screen_name']}%"))
    
    # 按时间排序
    query = query.order_by(Weibo.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 处理结果
    items = []
    for weibo, weibo_geom in pagination.items:
        item = weibo.to_dict()
        if weibo_geom:
            geom_data = weibo_geom.to_dict()
            item.update({
                'point': geom_data['point'],
                'geometry': geom_data['geometry']
            })
        items.append(item)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })

# 根据面范围查询在范围内的点位
@app.route('/api/weibo_geom/within/<id>', methods=['GET'])
def get_points_within(id):
    # 获取指定 id 的 geometry 记录
    geometry_record = WeiboGeom.query.get(id)
    if not geometry_record or not geometry_record.geometry:
        return jsonify({
            'code': 404,
            'message': '指定的 geometry 不存在',
            'data': None
        }), 404

    # 构建查询
    query = db.session.query(Weibo, WeiboGeom).outerjoin(
        WeiboGeom, Weibo.id == WeiboGeom.id
    )

    # 使用 geometry 查询在范围内的点位
    points_within = query.filter(
        func.ST_Within(WeiboGeom.point, geometry_record.geometry)
    ).all()

    # 返回结果  
    result = []
    for weibo, weibo_geom in points_within:
        item = weibo.to_dict()
        if weibo_geom:
            geom_data = weibo_geom.to_dict()
            item.update({
                'point': geom_data['point'],
                'geometry': []
            })
        result.append(item)
    
    if not result:
        return jsonify({
            'code': 404,
            'message': '指定的微博不存在',
            'data': None
        }), 404

    # 返回微博数据
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': result
    })
# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': '请求的资源不存在',
        'data': None
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'code': 500,
        'message': '服务器内部错误',
        'data': None
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8006) 