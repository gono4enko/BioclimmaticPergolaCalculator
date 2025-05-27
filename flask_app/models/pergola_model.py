"""
Модели данных, связанные с перголами.
"""
import datetime
from sqlalchemy.dialects.postgresql import JSON
from .. import db

class Pergola(db.Model):
    """Модель для представления перголы."""
    
    __tablename__ = 'pergolas'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Основные параметры
    type = db.Column(db.String(50), nullable=False)  # B500NEW, B700NEW, B600
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    modules = db.Column(db.Integer, nullable=False, default=1)
    lamella_size = db.Column(db.String(10), nullable=False)  # 200, 250, PIR
    
    # Опции и цены
    options = db.Column(JSON, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False, default=0)
    total_price_after_discount = db.Column(db.Float, nullable=False)
    
    # Связанные файлы
    pdf_path = db.Column(db.String(255), nullable=True)
    
    def __init__(self, **kwargs):
        super(Pergola, self).__init__(**kwargs)
    
    def __repr__(self):
        return f"<Pergola {self.type} {self.width}x{self.length}м {self.id}>"
    
    def to_dict(self):
        """Преобразует модель в словарь для API."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'type': self.type,
            'width': self.width,
            'length': self.length,
            'modules': self.modules,
            'lamella_size': self.lamella_size,
            'options': self.options,
            'total_price': self.total_price,
            'discount': self.discount,
            'total_price_after_discount': self.total_price_after_discount,
            'pdf_path': self.pdf_path
        }


class PriceData(db.Model):
    """Модель для хранения данных о ценах."""
    
    __tablename__ = 'price_data'
    
    id = db.Column(db.Integer, primary_key=True)
    pergola_type = db.Column(db.String(50), nullable=False)
    lamella_size = db.Column(db.String(10), nullable=False)
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    modules = db.Column(db.Integer, nullable=False, default=1)
    
    def __init__(self, **kwargs):
        super(PriceData, self).__init__(**kwargs)
    
    def __repr__(self):
        return f"<PriceData {self.pergola_type} {self.lamella_size} {self.width}x{self.length}м>"
    
    @classmethod
    def get_by_dimensions(cls, pergola_type, lamella_size, width, length):
        """
        Получает запись с ценой по указанным размерам.
        
        Args:
            pergola_type (str): Тип перголы
            lamella_size (str): Размер ламели
            width (float): Ширина перголы
            length (float): Длина перголы
            
        Returns:
            PriceData: Найденная запись или None
        """
        return cls.query.filter_by(
            pergola_type=pergola_type,
            lamella_size=lamella_size,
            width=width,
            length=length
        ).first()


class CalculationHistory(db.Model):
    """Модель для хранения истории расчетов."""
    
    __tablename__ = 'calculation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Основные параметры
    pergola_type = db.Column(db.String(50), nullable=False)
    width = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    modules = db.Column(db.Integer, nullable=False, default=1)
    lamella_size = db.Column(db.String(10), nullable=False)
    
    # Результаты расчета
    options = db.Column(JSON, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, nullable=False, default=0)
    total_price_after_discount = db.Column(db.Float, nullable=False)
    
    # Идентификатор перголы, если сохранена
    pergola_id = db.Column(db.Integer, db.ForeignKey('pergolas.id'), nullable=True)
    pergola = db.relationship('Pergola', backref=db.backref('calculations', lazy=True))
    
    def __init__(self, **kwargs):
        super(CalculationHistory, self).__init__(**kwargs)
    
    def __repr__(self):
        return f"<CalculationHistory {self.pergola_type} {self.width}x{self.length}м {self.id}>"