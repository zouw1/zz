from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt

# 数据库连接配置
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:zw20021216120@localhost/ai_image_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建模型基类
Base = declarative_base()

class User(Base):
    """
    用户数据模型
    Attributes:
        id: 用户ID，主键
        username: 用户名，唯一
        email: 邮箱，唯一
        hashed_password: 加密后的密码
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行加密
        Args:
            password: 原始密码
        Returns:
            加密后的密码字符串
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """
        验证密码是否正确
        Args:
            password: 待验证的密码
        Returns:
            密码是否匹配
        """
        return bcrypt.checkpw(password.encode('utf-8'), 
                            self.hashed_password.encode('utf-8'))

# 创建数据库表
Base.metadata.create_all(bind=engine) 