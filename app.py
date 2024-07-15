from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409
    
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    """
    Create a new blog post.
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    new_post = BlogPost(title=title, content=content, user_id=1)  # Replace with your user_id logic
    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        'id': new_post.id,
        'title': new_post.title,
        'content': new_post.content,
        'user_id': new_post.user_id
    }), 201

@app.route('/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts.
    """
    posts = BlogPost.query.all()
    output = [{'id': post.id, 'title': post.title, 'content': post.content, 'user_id': post.user_id} for post in posts]
    return jsonify(output), 200

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return jsonify({'id': post.id, 'title': post.title, 'content': post.content, 'user_id': post.user_id}), 200

@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    data = request.get_json()
    post = BlogPost.query.get_or_404(post_id)
    current_user = get_jwt_identity()['username']
    
    if post.user.username != current_user:
        return jsonify({'message': 'You are not authorized to update this post'}), 403
    
    post.title = data['title']
    post.content = data['content']
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'}), 200

@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    current_user = get_jwt_identity()['username']
    
    if post.user.username != current_user:
        return jsonify({'message': 'You are not authorized to delete this post'}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)