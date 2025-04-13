from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from datetime import datetime  # 导入 datetime

db = SQLAlchemy()

# 微博地理信息模型
class WeiboGeom(db.Model):
    __tablename__ = 'weibo_geom'
    
    id = db.Column(db.String(20), primary_key=True)
    bid = db.Column(db.String(12), nullable=False)
    ip = db.Column(db.String(100))
    
    point = db.Column(Geometry('POINT', srid=4326))
    geometry = db.Column(Geometry('GEOMETRY', srid=4326))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增 created_at 字段
    
    def to_dict(self):
        return {
            'id': self.id,
            'bid': self.bid,
            'ip': self.ip,
            'created_at': self.created_at.isoformat() if self.created_at else None,  # 格式化时间
            'point': mapping(to_shape(self.point)) if self.point else None,
            'geometry': mapping(to_shape(self.geometry)) if self.geometry else None
        }
    
    def to_simple_dict(self):
        """返回简化的数据，只包含 IP 和经纬度"""
        point = to_shape(self.point) if self.point else None
        return {
            'id': self.id,
            'lng': point.x if point else None,
            'lat': point.y if point else None
        } 