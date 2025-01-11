from flask import Flask, logging, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from enum import Enum

# Initialize logging
logging.basicConfig(level=logging.INFO)

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
@app.route('/experiments', methods=['POST'])
def create_experiment():
    data = request.json
    try:
        new_experiment = Experiment(
            run_id=data['run_id'],
            dataset=data['dataset'],
            model=data['model'],
            learning_rate=data['learning_rate'],
            batch_size=data['batch_size'],
            num_epochs=data['num_epochs']
        )
        db.session.add(new_experiment)
        db.session.commit()
        logging.info(f"Experiment {data['run_id']} created successfully.")
        return jsonify({"message": "Experiment created successfully!"}), 201
    except Exception as e:
        logging.error(f"Error creating experiment: {str(e)}")
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
    logging.info("Retrieved all experiments.")
    return jsonify(result), 200 

#Update endpoint to update the status of the experiment
@app.route('/experiments/<string:run_id>', methods = ['PUT'])
def update_experiment(run_id):  
    data = request.json
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
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
        logging.info(f"Experiment {run_id} updated successfully.")
        return jsonify({"message": "Experiment updated successfully."}), 200
    except Exception as e:
        logging.error(f"Error updating experiment {run_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    
#Delete endpoint to delete an experiment
@app.route('/experiments/<string:run_id>', methods = ['DELETE'])
def delete_experiment(run_id):
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
        return jsonify({"error": "Experiment not found."}), 404
    try: 
        db.session.delete(experiment)
        db.session.commit()
        logging.info(f"Experiment {run_id} deleted successfully.")
        return jsonify({"message": "Experiment deleted successfully."}), 200
    except Exception as e:
        logging.error(f"Error deleting experiment {run_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    
#Status endpoint to monitor the status 
@app.route('/experiments/<string:run_id>/status', methods = ['GET'])
def get_experiment_status(run_id): 
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
        return jsonify({"error": "Experiment not found."}), 404
    result = {
        "run_id": experiment.run_id,
        "status": experiment.status.value,
        "iterations": experiment.iterations,
        "started_at": experiment.started_at
    }
    logging.info(f"Status for experiment {run_id} retrieved successfully.")
    return jsonify(result), 200

#Metrics endpoint to get the metrics of the experiment
@app.route('/experiments/<string:run_id>/metrics', methods = ['GET'])
def get_experiment_metrics(run_id):
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
        return jsonify({"error": "Experiment not found."}), 404
    result = {
        "run_id": experiment.run_id,
        "ap": experiment.ap,
        "ap50": experiment.ap50,
        "ap75": experiment.ap75,
        "aps": experiment.aps,
        "apm": experiment.apm,
        "apl": experiment.apl,
        "total_loss": experiment.total_loss,
        "cls_loss": experiment.cls_loss,
        "bbox_loss": experiment.bbox_loss,
        "mask_loss": experiment.mask_loss
    }
    logging.info(f"Metrics for experiment {run_id} retrieved successfully.")
    return jsonify(result), 200

#Automatic update Endpoint to live update the status of the experiment
@app.route('/experiments/<string:run_id>/update', methods = ['POST'])
def update_experiment_live(run_id):
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
        return jsonify({"error": "Experiment not found."}), 404
    data = request.json 
    if data is None: 
        logging.error("No data provided for live update.")
        return jsonify({"error": "No data provided."}), 400
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
        logging.info(f"Experiment {run_id} updated successfully.")
        return jsonify({"message": "Experiment updated successfully."}), 200
    except Exception as e:
        logging.error(f"Error updating experiment {run_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400

#Comparison endpoint 
@app.route('/experiments/compare', methods = ['GET'])
def compare_experiments():
    status_filter = request.args.get('status')
    sort_by = request.args.get('sort_by', 'run_id')
    order = request.args.get('order', 'desc')
    limit = request.args.get('limit', 10, type=int)
    
    valid_sort_fields = [
        'id', 'run_id', 'dataset', 'model', 'status',
        'learning_rate', 'batch_size', 'num_epochs',
        'ap', 'ap50', 'ap75', 'aps', 'apm', 'apl',
        'total_loss', 'cls_loss', 'bbox_loss', 'mask_loss', 'iterations'
    ]

    if sort_by not in valid_sort_fields:
        logging.error("Invalid sort_by field.")
        return jsonify({"error": "Invalid sort_by field."}), 400
    
    query = Experiment.query
    
    if status_filter:
        try: 
            status_enum = StatusEnum(status_filter)
            query = query.filter_by(status = status_enum)
        except ValueError:
            logging.error("Invalid status value.")
            return jsonify({"error": "Invalid status value."}), 400
    
    if order == 'asc': 
        query = query.order_by(getattr(Experiment, sort_by).asc())
    else:
        query = query.order_by(getattr(Experiment, sort_by).desc())

    if limit: 
        query = query.limit(limit)
        
    experiments = query.all()
    result = []
    for exp in experiments: 
        result.append({
            "id": exp.id,
            "run_id": exp.run_id,
            "dataset": exp.dataset,
            "model": exp.model,
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
            "mask_loss": exp.mask_loss,
            "iterations": exp.iterations
        })
    logging.info("Compared experiments.")
    return jsonify(result), 200


@app.route('/')
def hello():
    return "Welcome to MiniML - The Machine Learning Experiment Tracker!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)