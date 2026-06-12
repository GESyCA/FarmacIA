from flask import Flask
from routes import bula_routes
from routes import mauq_routes
from models import db
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bula_routes.bp)
    app.register_blueprint(mauq_routes.bp)

    # Configuração do banco de dados SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///remedios_chat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa o DB com a aplicação
    db.init_app(app)
    
    # Configura o Flask-Migrate para gerenciar as alterações no schema do DB
    migrate = Migrate(app, db)
    
    # Cria as tabelas do banco de dados se não existirem
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)