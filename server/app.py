from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages]), 200

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.get_or_404(id)
    return jsonify(message.to_dict()), 200

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()  # Get the JSON data from the request
    if not data or not data.get('body') or not data.get('username'):
        return jsonify({"error": "Missing required fields: 'body' and 'username'"}), 400
    
    new_message = Message(
        body=data['body'],
        username=data['username']
    )
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()  # Get the JSON data from the request
    message = Message.query.get_or_404(id)  # Find the message by ID
    
    if not data or not data.get('body'):
        return jsonify({"error": "Missing required field: 'body'"}), 400
    
    # Update the message body
    message.body = data['body']
    db.session.commit()  # Commit the changes to the database

    return jsonify(message.to_dict()), 200  # Return the updated message as JSON

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)  # Find the message by ID
    db.session.delete(message)  # Delete the message
    db.session.commit()  # Commit the deletion to the database

    return '', 204

if __name__ == '__main__':
    app.run(port=5555)
