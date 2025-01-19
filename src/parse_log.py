import re 

def parse_log_content(log_content): 
    parsed_data = {
        'ap': 0.0,
        'ap50': None, 
        'ap75': None,
        'aps': None,
        'apm': None,
        'apl': None,
        'total_loss': None,
        'loss_cls': None,
        'loss_box_reg': None,
        'loss_rpn_cls': None,
        'loss_rpn_loc': None,
        'iterations': None,
        'learning_rate': None,
        'batch_size': None,
    }
    
    #Define regex patterns to extract metrics
    ap_pattern = re.compile(r'Average Precision  \(AP\) @\[ IoU=0.50:0.95 \| area=   all \| maxDets=100 \] = ([0-9.]+)')
    ap50_pattern = re.compile(r'Average Precision\s*\(AP\)\s*@\[ IoU=0.50\s*\|\s*area=\s*all\s*\|\s*maxDets=100\s*\]\s*=\s*([0-9.]+)')
    ap75_pattern = re.compile(r'Average Precision\s*\(AP\)\s*@\[ IoU=0.75\s*\|\s*area=\s*all\s*\|\s*maxDets=100\s*\]\s*=\s*([0-9.]+)')
    aps_pattern = re.compile(r'Average Precision\s*\(AP\)\s*@\[ IoU=0.50:0.95\s*\|\s*area=\s*small\s*\|\s*maxDets=100\s*\]\s*=\s*([0-9.]+)')
    apm_pattern = re.compile(r'Average Precision\s*\(AP\)\s*@\[ IoU=0.50:0.95\s*\|\s*area=\s*medium\s*\|\s*maxDets=100\s*\]\s*=\s*([0-9.]+)')
    apl_pattern = re.compile(r'Average Precision\s*\(AP\)\s*@\[ IoU=0.50:0.95\s*\|\s*area=\s*large\s*\|\s*maxDets=100\s*\]\s*=\s*([0-9.]+)')
    total_loss_pattern = re.compile(r'total_loss: ([0-9.]+)')
    loss_cls_pattern = re.compile(r'loss_cls: ([0-9.]+)')
    loss_box_reg_pattern = re.compile(r'loss_box_reg: ([0-9.]+)')
    loss_rpn_cls_pattern = re.compile(r'loss_rpn_cls: ([0-9.]+)')
    loss_rpn_loc_pattern = re.compile(r'loss_rpn_loc: ([0-9.]+)')
    iterations_pattern = re.compile(r'iter: ([0-9]+)')
    learning_rate_pattern = re.compile(r'lr: ([0-9.]+)')
    batch_size_pattern = re.compile(r'batch_size=([0-9]+)')
    
    lines = log_content.splitlines()
    best_ap_line_index = 0
    iterations_line_index = 0
    
    #Search for best AP
    for i, line in enumerate(lines):
        ap_match = ap_pattern.search(line)
        if ap_match: 
            current_ap = float(ap_match.group(1))
            if current_ap > parsed_data['ap']: 
                parsed_data['ap'] = current_ap
                best_ap_line_index = i
                
    for j in range(best_ap_line_index, -1, -1): 
        iterations_match = iterations_pattern.search(lines[j])
        if iterations_match: 
            iterations_line_index = j
            break
                
    if best_ap_line_index is not None:
        for line in lines[best_ap_line_index:]:
            if parsed_data['ap50'] is None: 
                ap50_match = ap50_pattern.search(line)
                if ap50_match:
                    parsed_data['ap50'] = float(ap50_match.group(1))
            if parsed_data['ap75'] is None:
                ap75_match = ap75_pattern.search(line)
                if ap75_match:
                    parsed_data['ap75'] = float(ap75_match.group(1))
            if parsed_data['aps'] is None:
                aps_match = aps_pattern.search(line)
                if aps_match:
                    parsed_data['aps'] = float(aps_match.group(1))
            if parsed_data['apm'] is None:
                apm_match = apm_pattern.search(line)
                if apm_match:
                    parsed_data['apm'] = float(apm_match.group(1))
            if parsed_data['apl'] is None:
                apl_match = apl_pattern.search(line)
                if apl_match:
                    parsed_data['apl'] = float(apl_match.group(1))
                    
        for line in lines[iterations_line_index:best_ap_line_index]:
            if parsed_data['total_loss'] is None:
                total_loss_match = total_loss_pattern.search(line)
                if total_loss_match:
                    parsed_data['total_loss'] = float(total_loss_match.group(1))
            if parsed_data['loss_cls'] is None:
                loss_cls_match = loss_cls_pattern.search(line)
                if loss_cls_match:
                    parsed_data['loss_cls'] = float(loss_cls_match.group(1))
            if parsed_data['loss_box_reg'] is None:
                loss_box_reg_match = loss_box_reg_pattern.search(line)
                if loss_box_reg_match:
                    parsed_data['loss_box_reg'] = float(loss_box_reg_match.group(1))
            if parsed_data['loss_rpn_cls'] is None:
                loss_rpn_cls_match = loss_rpn_cls_pattern.search(line)
                if loss_rpn_cls_match:
                    parsed_data['loss_rpn_cls'] = float(loss_rpn_cls_match.group(1))
            if parsed_data['loss_rpn_loc'] is None:
                loss_rpn_loc_match = loss_rpn_loc_pattern.search(line)
                if loss_rpn_loc_match:
                    parsed_data['loss_rpn_loc'] = float(loss_rpn_loc_match.group(1))
            if parsed_data['iterations'] is None:
                iterations_match = iterations_pattern.search(line)
                if iterations_match:
                    parsed_data['iterations'] = int(iterations_match.group(1))
            if parsed_data['learning_rate'] is None:
                learning_rate_match = learning_rate_pattern.search(line)
                if learning_rate_match:
                    parsed_data['learning_rate'] = float(learning_rate_match.group(1))
            if parsed_data['batch_size'] is None:
                batch_size_match = batch_size_pattern.search(line)
                if batch_size_match:
                    parsed_data['batch_size'] = int(batch_size_match.group(1))
    return parsed_data
    