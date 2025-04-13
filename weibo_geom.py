from flask import Blueprint, jsonify, request
from sqlalchemy import func
from datetime import datetime
from models import db, WeiboGeom

# 创建蓝图
weibo_geom_bp = Blueprint('weibo_geom', __name__)

# 获取单条记录
@weibo_geom_bp.route('/api/weibo_geom/<id>', methods=['GET'])
def get_weibo_geom(id):
    """获取单条微博地理信息"""
    weibo_geom = WeiboGeom.query.get(id)
    if weibo_geom:
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': weibo_geom.to_dict()
        })
    return jsonify({
        'code': 404,
        'message': '记录不存在',
        'data': None
    }), 404

# 获取记录列表
@weibo_geom_bp.route('/api/weibo_geom', methods=['GET'])
def get_weibo_geom_list():
    """获取微博地理信息列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = WeiboGeom.query
    
    # 按IP筛选
    if 'ip' in request.args:
        query = query.filter(WeiboGeom.ip == request.args['ip'])
    
    # 空间查询
    if 'lat' in request.args and 'lng' in request.args:
        lat = float(request.args['lat'])
        lng = float(request.args['lng'])
        radius = float(request.args.get('radius', 1))  # 默认1公里
        
        # 创建点
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
        # 创建缓冲区
        buffer = func.ST_Buffer(point, radius/111.32)  # 将公里转换为度（粗略估算）
        
        # 查询在缓冲区内的点
        query = query.filter(func.ST_Within(WeiboGeom.point, buffer))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
    })

# 空间统计
@weibo_geom_bp.route('/api/weibo_geom/stats', methods=['GET'])
def get_weibo_geom_stats():
    """获取微博地理信息统计"""
    # 获取总记录数
    total = WeiboGeom.query.count()
    
    # 获取有地理信息的记录数
    with_geom = WeiboGeom.query.filter(WeiboGeom.point.isnot(None)).count()
    
    # 获取有IP信息的记录数
    with_ip = WeiboGeom.query.filter(WeiboGeom.ip.isnot(None)).count()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'total': total,
            'with_geometry': with_geom,
            'with_ip': with_ip
        }
    })

# 空间聚合
@weibo_geom_bp.route('/api/weibo_geom/aggregate', methods=['GET'])
def get_weibo_geom_aggregate():
    """获取微博地理信息聚合数据"""
    # 按IP分组统计
    ip_stats = db.session.query(
        WeiboGeom.ip,
        func.count(WeiboGeom.id).label('count')
    ).group_by(WeiboGeom.ip).all()
    
    # 转换为字典列表
    ip_stats_list = [{'ip': ip, 'count': count} for ip, count in ip_stats if ip]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'ip_stats': ip_stats_list
        }
    })

# 获取所有数据的 ID 和经纬度
@weibo_geom_bp.route('/api/weibo_geom/all_points', methods=['GET'])
def get_all_points():
    """获取所有数据的 ID 和经纬度信息"""
    # 只查询有地理信息的记录
    query = WeiboGeom.query.filter(WeiboGeom.point.isnot(None))
    
    # 如果指定了 ID，则按 ID 筛选
    if 'id' in request.args:
        query = query.filter(WeiboGeom.id == request.args['id'])
    
    # 获取所有记录
    items = query.all()
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [item.to_simple_dict() for item in items],
            'total': len(items)
        }
    })

# 按 IP 分组统计
@weibo_geom_bp.route('/api/weibo_geom/ip_stats', methods=['GET'])
def get_ip_stats():
    """获取按 IP 分组的统计信息"""
    # 执行分组统计查询
    page = request.args.get('page', 1, type=int)  # 获取当前页码，默认为1
    per_page = request.args.get('per_page', 8, type=int)  # 获取每页记录数，默认为10

    # 执行分组统计查询并按value降序排序
    stats_query = db.session.query(
        WeiboGeom.ip.label('name'),
        func.count(WeiboGeom.id).label('value')
    ).group_by(WeiboGeom.ip).order_by(func.count(WeiboGeom.id).desc())
    #查询总数
    total = stats_query.count()
    # 执行分页
    stats = stats_query.paginate(page=page, per_page=per_page, error_out=False).items
    
    # 转换为字典列表
    stats_list = [{'name': ip, 'value': count} for ip, count in stats if ip]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': stats_list,
        'total': total
    })
