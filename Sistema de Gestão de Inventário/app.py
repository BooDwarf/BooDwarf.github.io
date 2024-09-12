from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventario.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chaveSecretaLembraDeTrocarDepois'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='testuser').first():
            hashed_password = generate_password_hash('testpassword', method='pbkdf2:sha256', salt_length=8)
            test_user = User(username='testuser', password=hashed_password)
            db.session.add(test_user)
            db.session.commit()

create_db()

@app.route('/')
@login_required
def index():
    categorias = Categoria.query.all()
    return render_template('index.html', categorias=categorias)

@app.route('/add_categoria', methods=['POST'])
@login_required
def add_categoria():
    nome = request.form['nome']
    categoria = Categoria(nome=nome)
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_produto', methods=['POST'])
@login_required
def add_produto():
    nome = request.form['nome']
    quantidade = request.form['quantidade']
    preco = request.form['preco']
    categoria_id = request.form['categoria_id']
    produto = Produto(nome=nome, quantidade=quantidade, preco=preco, categoria_id=categoria_id)
    db.session.add(produto)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Usuário ou senha inválidos'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#colocar o site no ar
#se importado por outro arquivo, precisa iniciar da principal se não, 
#não vai rodar.
if __name__ == '__main__':
    app.run(debug=True)

#servidor do heroku