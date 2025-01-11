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
    
#Endpoints 
# Endpoint to create a new experiment
@app.route('/experiments', methods = ['POST'])
def create_experiment():
    data = request.json   
    try:
        new_experiment = Experiment(
            run_id = data['run_id'],
            dataset = data['dataset'],
            model = data['model'],
            learning_rate = data['learning_rate'],
            batch_size = data['batch_size'],
            num_epochs = data['num_epochs']
        )
        db.session.add(new_experiment)
        db.session.commit()
        return jsonify({"message": "Experiment created successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Read endpoint to get all the experiments
@app.route('/experiments', methods = ['GET'])
def get_experiments(): 
    experiments = Experiment.query.all()
    result = []
    for exp in experiments: 
        result.append({
            "id": exp.id,
            "run_id": exp.run_id,
            "dataset": exp.dataset,
            "model": exp.model,
            "started_at": exp.started_at,
            "iterations": exp.iterations,
            "status": exp.status.value,
            "learning_rate": exp.learning_rate,
            "batch_size": exp.batch_size,
            "num_epochs": exp.num_epochs,
            "ap": exp.ap,
            "ap50": exp.ap50,
            "ap75": exp.ap75,
            "aps": exp.aps,
            "apm": exp.apm,
            "apl": exp.apl,
            "total_loss": exp.total_loss,
            "cls_loss": exp.cls_loss,
            "bbox_loss": exp.bbox_loss,
            "mask_loss": exp.mask_loss
        })
    return jsonify(result), 200 

#Update endpoint to update the status of the experiment
@app.route('/experiments/<string:run_id>', methods = ['PUT'])
def update_experiment(run_id):  
    data = request.json
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        return jsonify({"error": "Experiment not found."}), 404
    try: 
        if 'status' in data: 
            experiment.status = StatusEnum(data['status'])
        if 'iterations' in data: 
            experiment.iterations = data['iterations']
        if 'ap' in data: 
            experiment.ap = data['ap']
        if 'ap50' in data: 
            experiment.ap50 = data['ap50']
        if 'ap75' in data:
            experiment.ap75 = data['ap75']
        if 'aps' in data:
            experiment.aps = data['aps']
        if 'apm' in data:
            experiment.apm = data['apm']
        if 'apl' in data:
            experiment.apl = data['apl']
        if 'total_loss' in data:
            experiment.total_loss = data['total_loss']
        if 'cls_loss' in data:
            experiment.cls_loss = data['cls_loss']
        if 'bbox_loss' in data:
            experiment.bbox_loss = data['bbox_loss']
        if 'mask_loss' in data:
            experiment.mask_loss = data['mask_loss']
        db.session.commit()
        return jsonify({"message": "Experiment updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
#Delete endpoint to delete an experiment
@app.route('/experiments/<string:run_id>', methods = ['DELETE'])
def delete_experiment(run_id):
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        return jsonify({"error": "Experiment not found."}), 404
    try: 
        db.session.delete(experiment)
        db.session.commit()
        return jsonify({"message": "Experiment deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)