from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    nome_remedio = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Conversation {self.id}>'

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    
    # role pode ser 'user' ou 'llm'
    role = db.Column(db.String(20), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.relationship('Feedback', backref='message', uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Message {self.id} role={self.role}>'

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False, unique=True)

    # Avaliação
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback for Message {self.message_id} - Score: {self.score}>'

class MauqQuestions(db.Model):
    __tablename__ = 'mauq_questions'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    dimension = db.Column(db.Integer, nullable=False)
    inverted = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MauqQuestion number={self.number}>'
