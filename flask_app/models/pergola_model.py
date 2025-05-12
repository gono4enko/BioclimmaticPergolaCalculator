"""
Модели данных для пергол и связанных с ними объектов.
"""
import json
import datetime
from .. import db

class Pergola(db.Model):
    """Модель перголы в базе данных."""
    __tablename__ = 'pergolas'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # B500NEW, B700NEW, B600
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    modules = db.Column(db.Integer, nullable=False, default=1)
    lamella_size = db.Column(db.String(10), nullable=False)  # 200, 250, PIR
    options_json = db.Column(db.Text, nullable=False)  # JSON с выбранными опциями
    total_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    total_price_after_discount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    pdf_path = db.Column(db.String(255))
    
    @property
    def options(self):
        """Получение опций из JSON"""
        return json.loads(self.options_json)
    
    @options.setter
    def options(self, options_dict):
        """Сохранение опций в JSON"""
        self.options_json = json.dumps(options_dict)
    
    def to_dict(self):
        """Конвертация объекта в словарь для API"""
        return {
            'id': self.id,
            'type': self.type,
            'width': self.width,
            'length': self.length,
            'modules': self.modules,
            'lamella_size': self.lamella_size,
            'options': self.options,
            'total_price': self.total_price,
            'discount': self.discount,
            'total_price_after_discount': self.total_price_after_discount,
            'created_at': self.created_at.isoformat(),
            'pdf_path': self.pdf_path
        }

class PriceData(db.Model):
    """Модель для хранения ценовых данных для разных типов пергол."""
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    pergola_type = db.Column(db.String(20), nullable=False)  # B500NEW, B700NEW, B600
    lamella_size = db.Column(db.String(10), nullable=False)  # 200, 250, PIR
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    modules = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f"<PriceData {self.pergola_type}-{self.lamella_size} {self.width}x{self.length}m: {self.price}>"