
from flask import Flask, Response, logging, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
from enum import Enum
from src.parse_log import parse_log_content

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
    dataset = db.Column(db.String(200), nullable = True)
    model = db.Column(db.String(200), nullable = True)
    started_at = db.Column(db.DateTime, default = datetime.now)
    iterations = db.Column(db.Integer, nullable = False, default = 0)
    status = db.Column(db.Enum(StatusEnum), nullable = True, default = 'RUNNING')
    
    #Hyperparameters
    learning_rate = db.Column(db.Float, nullable = False)
    batch_size = db.Column(db.Integer, nullable = False, default = 0)
    num_epochs = db.Column(db.Integer, nullable = True)
    
    #Metrics ( Average Precision)
    ap = db.Column(db.Float, nullable = False, default = 0.0)
    ap50 = db.Column(db.Float, nullable = False, default = 0.0)
    ap75 = db.Column(db.Float, nullable = False, default = 0.0)
    aps = db.Column(db.Float, nullable = False, default = 0.0)
    apm = db.Column(db.Float, nullable = False, default = 0.0)
    apl = db.Column(db.Float, nullable = False, default = 0.0)
    
    #Metrics (Loss)
    total_loss = db.Column(db.Float, nullable = False, default = 0.0)
    loss_cls = db.Column(db.Float, nullable = False, default = 0.0)
    loss_box_reg = db.Column(db.Float, nullable = False, default = 0.0)
    loss_rpn_cls = db.Column(db.Float, nullable = False, default = 0.0)
    loss_rpn_loc = db.Column(db.Float, nullable = False, default = 0.0)
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
            "loss_cls": exp.loss_cls,
            "loss_box_reg": exp.loss_box_reg,
            "loss_rpn_cls": exp.loss_rpn_cls,
            "loss_rpn_loc": exp.loss_rpn_loc,
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
        if 'loss_cls' in data:
            experiment.loss_cls = data['loss_cls']
        if 'loss_box_reg' in data:
            experiment.loss_box_reg = data['loss_box_reg']
        if 'loss_rpn_cls' in data:
            experiment.loss_rpn_cls = data['loss_rpn_cls']
        if 'loss_rpn_loc' in data:
            experiment.loss_rpn_loc = data['loss_rpn_loc']
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

#Information endpoint to get the information of the experiment
@app.route('/experiments/<string:run_id>/info', methods = ['GET'])
def get_experiment_info(run_id):
    experiment = Experiment.query.filter_by(run_id = run_id).first()
    if experiment is None: 
        logging.warning(f"Experiment {run_id} not found.")
        return jsonify({"error": "Experiment not found."}), 404
    result = {
        "run_id": experiment.run_id,
        "dataset": experiment.dataset,
        "model": experiment.model,
        "learning_rate": experiment.learning_rate,
        "batch_size": experiment.batch_size,
        "num_epochs": experiment.num_epochs
    }
    logging.info(f"Information for experiment {run_id} retrieved successfully.")
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
        "loss_cls": experiment.loss_cls,
        "loss_box_reg": experiment.loss_box_reg,
        "loss_rpn_cls": experiment.loss_rpn_cls,
        "loss_rpn_loc": experiment.loss_rpn_loc,
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
        if 'loss_cls' in data:
            experiment.loss_cls = data['loss_cls']
        if 'loss_box_reg' in data:
            experiment.loss_box_reg = data['loss_box_reg']
        if 'loss_rpn_cls' in data:
            experiment.loss_rpn_cls = data['loss_rpn_cls']
        if 'loss_rpn_loc' in data:
            experiment.loss_rpn_loc = data['loss_rpn_loc']
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
        'total_loss', 'loss_cls', 'loss_box_reg', 'loss_rpn_cls', 'loss_rpn_loc' 'mask_loss', 'iterations'
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
            "loss_cls": exp.loss_cls,
            "loss_box_reg": exp.loss_box_reg,
            "loss_rpn_cls": exp.loss_rpn_cls,
            "loss_rpn_loc": exp.loss_rpn_loc,
            "mask_loss": exp.mask_loss,
            "iterations": exp.iterations
        })
    logging.info("Compared experiments.")
    return jsonify(result), 200

#Live Logging for Output 
logs = {}

@app.route('/experiments/<string:run_id>/logs', methods = ['POST'])
def get_experiment_logs(run_id): 
    #Get logs from workstation and save them temporarily
    data = request.json
    log_entry = data.get('log')
    if not log_entry: 
        return jsonify({"error": "No log entry provided."}), 400
    
    if run_id not in logs: 
        logs[run_id] = []
    logs[run_id].append(log_entry)
    
    return jsonify({"message": "Log received successfully."}), 200

@app.route('/experiments/<string:run_id>/logs', methods = ['GET'])
def stream_logs(run_id):
    def generate():
        if run_id in logs:
            for log in logs[run_id]:
                yield log + '\n'
    
    return Response(generate(), mimetype='text/plain')

#Upload endpoints 
@app.route('/experiments/parse-log', methods=['POST'])
def parse_log():
    file = request.files.get('file')
    if not file:
        logging.error("No file provided for parsing.")
        return jsonify({"error": "No file provided."}), 400

    try:
        content = file.read().decode('utf-8')

        parsed_data = parse_log_content(content)

        logging.info("Log parsed successfully.")
        return jsonify(parsed_data), 200
    except UnicodeDecodeError:
        logging.error("File could not be decoded. Ensure it's a valid text file.")
        return jsonify({"error": "File could not be decoded. Ensure it's a valid text file."}), 400
    except Exception as e:
        logging.error(f"Error parsing log file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/experiments/upload-run', methods = ['POST'])
def create_run(): 
    data = request.json
    if not data:
        logging.error("No JSON data provided.")
        return jsonify({"error": "No JSON data provided."}), 400

    run_id = data.get('run_id')
    if not run_id:
        logging.error("Run ID is required.")
        return jsonify({"error": "Run ID is required."}), 400

    try: 
        new_experiment = Experiment(
            run_id=run_id,
            dataset=data.get('dataset'),
            model=data.get('model'),
            learning_rate=data.get('learning_rate'),
            batch_size=data.get('batch_size'),
            num_epochs=data.get('num_epochs'),
            ap=data.get('ap'),
            ap50=data.get('ap50'),
            ap75=data.get('ap75'),
            aps=data.get('aps'),
            apm=data.get('apm'),
            apl=data.get('apl'),
            total_loss=data.get('total_loss'),
            loss_cls=data.get('loss_cls'),
            loss_box_reg=data.get('loss_box_reg'),
            loss_rpn_cls=data.get('loss_rpn_cls'),
            loss_rpn_loc=data.get('loss_rpn_loc'),
            iterations=data.get('iterations'),
            mask_loss=data.get('mask_loss')
        )
        db.session.add(new_experiment)
        db.session.commit()
        
        logging.info(f"Experiment {data['run_id']} created successfully.")
        return jsonify({"message": "Experiment created successfully!"}), 201
    except Exception as e:
        logging.error(f"Error creating experiment: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/')
def hello():
    return "Welcome to MiniML - The Machine Learning Experiment Tracker!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)