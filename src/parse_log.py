import re 

def parse_log_content(log_content): 
    parsed_data = {}
    
    #Extract Average Precision metrics 
    ap_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.50:0.95 \| area=   all \| maxDets=100 \] = ([0-9.]+)', log_content)
    ap50_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.50      \| area=   all \| maxDets=100 \] = ([0-9.]+)', log_content)
    ap75_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.75      \| area=   all \| maxDets=100 \] = ([0-9.]+)', log_content)
    aps_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.50:0.95 \| area= small \| maxDets=100 \] = ([0-9.]+)', log_content)
    apm_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.50:0.95 \| area=medium \| maxDets=100 \] = ([0-9.]+)', log_content)
    apl_match = re.search(r'Average Precision  \(AP\) @\[ IoU=0.50:0.95 \| area= large \| maxDets=100 \] = ([0-9.]+)', log_content)
    
    parsed_data['ap'] = float(ap_match.group(1)) if ap_match else None
    parsed_data['ap50'] = float(ap50_match.group(1)) if ap50_match else None
    parsed_data['ap75'] = float(ap75_match.group(1)) if ap75_match else None
    parsed_data['aps'] = float(aps_match.group(1)) if aps_match else None
    parsed_data['apm'] = float(apm_match.group(1)) if apm_match else None
    parsed_data['apl'] = float(apl_match.group(1)) if apl_match else None
    
    #Extract Loss metrics
    total_loss_match = re.search(r'total_loss: ([0-9.]+)', log_content)
    loss_cls_match = re.search(r'loss_cls: ([0-9.]+)', log_content)
    loss_box_reg_match = re.search(r'loss_box_reg: ([0-9.]+)', log_content)
    loss_rpn_cls_match = re.search(r'loss_rpn_cls: ([0-9.]+)', log_content)
    loss_rpn_loc_match = re.search(r'loss_rpn_loc: ([0-9.]+)', log_content)
    
    parsed_data['total_loss'] = float(total_loss_match.group(1)) if total_loss_match else None
    parsed_data['loss_cls'] = float(loss_cls_match.group(1)) if loss_cls_match else None
    parsed_data['loss_box_reg'] = float(loss_box_reg_match.group(1)) if loss_box_reg_match else None
    parsed_data['loss_rpn_cls'] = float(loss_rpn_cls_match.group(1)) if loss_rpn_cls_match else None
    parsed_data['loss_rpn_loc'] = float(loss_rpn_loc_match.group(1)) if loss_rpn_loc_match else None
    
    #Extract iterations
    iterations_match = re.search(r'iter: ([0-9]+)', log_content)
    parsed_data['iterations'] = int(iterations_match.group(1)) if iterations_match else None
    
    #Extract hyperparameters
    learning_rate_match = re.search(r'lr: ([0-9.]+)', log_content)
    batch_size_match = re.search(r'batch_size=([0-9]+)', log_content)
    
    
    parsed_data['learning_rate'] = float(learning_rate_match.group(1)) if learning_rate_match else None
    parsed_data['batch_size'] = int(batch_size_match.group(1)) if batch_size_match else None
    
    
    return parsed_data