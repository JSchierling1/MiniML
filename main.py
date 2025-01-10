from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('experiments.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enum class to define the status of the experiment
class StatusEnum(Enum): 
    RUNNING = 'Running'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    ABORTED = 'Aborted'
    
# Class Experiment to create the table in the database
class Experiment(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.String(200), nullable = False)
    dataset = db.Column(db.String(200), nullable = False)
    model = db.Column(db.String(200), nullable = False)
    started_at = db.Column(db.DateTime, default = datetime.now)
    iterations = db.Column(db.Integer, nullable = False, default = 0)
    status = db.Column(db.Enum(StatusEnum), nullable = False, default = 'Running')
    
    #Hyperparameters
    learning_rate = db.Column(db.Float, nullable = False)
    batch_size = db.Column(db.Integer, nullable = False)
    num_epochs = db.Column(db.Integer, nullable = False)
    
    #Metrics ( Average Precision)
    ap = db.Column(db.Float, nullable = False, default = 0.0)
    ap50 = db.Column(db.Float, nullable = False, default = 0.0)
    ap75 = db.Column(db.Float, nullable = False, default = 0.0)
    aps = db.Column(db.Float, nullable = False, default = 0.0)
    apm = db.Column(db.Float, nullable = False, default = 0.0)
    apl = db.Column(db.Float, nullable = False, default = 0.0)
    
    #Metrics (Loss)
    total_loss = db.Column(db.Float, nullable = False, default = 0.0)
    cls_loss = db.Column(db.Float, nullable = False, default = 0.0)
    bbox_loss = db.Column(db.Float, nullable = False, default = 0.0)
    mask_loss = db.Column(db.Float, nullable = True) # Optional metric for Instance Segmentation models
    
    
    
    
@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)