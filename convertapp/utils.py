import re
import copy
import csv


## Special characters to be aware of during dictionary application. Might need
# additional character addition. 
special_chars = [".", "+",  "'"]



## defining regex replacer
class REReplacer:
   def __init__(self, patterns):
      self.pattern = [(re.compile(regex.lower()), repl.lower()) for (regex, repl) in patterns]
   def replace(self, text):
    text = str(text)      
    s = text.lower()
    for (pattern, repl) in self.pattern:
        s = re.sub(pattern, repl, s)
    return s

def convert_special_character(line):
    flag = 0
    for i, word in enumerate(line):
        
        s = ''
        for c in word:
            if c in special_chars:
                flag = 1
                s = c
        if flag:
            rep = '\\' + s
            word = word.replace(s, rep)
            line[i] = word
            flag = 0
    return line


def create_pattern(path):
    new_dict = []
    with open(path, newline='') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            row = [w for w in row if w is not '']
            new_dict.append(convert_special_character(row))
    
    pattern_list = []
    for line in new_dict:
        ideal = line[0]
        for w in line[1:]:
            pattern_list.append(tuple([w, ideal]))
    
    rep_word = REReplacer(pattern_list)

    return rep_word




## funciton to process inch variations in Size feature. Might not be necessary if dictionary is applied
def strip_string(s):  
    s = str(s)
    # print(f"Printing value {s}")
    if "in" in s.split():
        s1 = s.replace("in", "").rstrip()
    elif "in." in s.split():
        s1 = s.replace("in.", "").rstrip()
    elif "inch" in s.split():
        s1 = s.replace("inch", "").rstrip()
    elif "inch." in s.split():
        s1 = s.replace("inch.", "").rstrip()
    else:
        s1 = s
    tmp = re.split("-| ", s1)
    tmp = list(filter(lambda x: x != "", tmp))
    if len(tmp) == 1 and "/" in tmp[0]:
        tmp_1 = tmp[0].split("/")
        num, denom = tmp_1[0], tmp_1[1]
        return float(num) / float(denom)
    if len(tmp) == 1:
        return float(tmp[0])
    if len(tmp) > 1:
        tmp_1 = float(tmp[0])
        tmp_2 = tmp[1].split("/")
        num, denom = tmp_2[0], tmp_2[1]
        dec = float(num) / float(denom)
        return tmp_1 + dec

    return float(tmp[0])


## for one, three and five best results
def find_labels(cat_feat_ind_dict, cat_lab, findings):
    tmp_feat = []
    tmp_lab = []
    tmp_conf = []

    for f in findings:
        lab = f[0]
        conf = f[1]
        label_ind = cat_feat_ind_dict[lab]
        label = cat_lab[label_ind]
        tmp_lab.append(label)
        tmp_conf.append(conf)
        tmp_feat.append(lab)

    return tmp_lab, tmp_conf, tmp_feat

## for multiple results
def find_multiple_labels(findings, reference_dict):
    
    res_dict = {}
    res_dict['confidence'] = {}
    
    for f in findings:       
        feat = f[0]
        conf = f[1]  
        print(f"Confidence in the function {conf}") 
        if conf == 100:
            res_dict['catalogue_feature'] = feat
            
            label = reference_dict[feat]
            res_dict['confidence']['100'] = label  ## in the reference dictionary, all the labels matched

            return res_dict
        
        elif conf < 100 and conf >= 85:
            label = copy.deepcopy(reference_dict[feat])  ## One of the most difficult problems
         
            if 'between_85_and_99' not in res_dict['confidence']:  
                res_dict['catalogue_feature'] = [feat]
                res_dict['confidence']['between_85_and_99'] = label
            else:
                
                res_dict['confidence']['between_85_and_99'].extend(label)
        elif conf >= 50 and conf <85:
            label = copy.deepcopy(reference_dict[feat])  ## One of the most difficult problems
         
            if 'between_50_and_85' not in res_dict['confidence']:  
                res_dict['catalogue_feature'] = [feat]
                res_dict['confidence']['between_50_and_85'] = label
            else:
                
                res_dict['confidence']['between_50_and_85'].extend(label)
        else:
            label = copy.deepcopy(reference_dict[feat])  ## One of the most difficult problems
         
            if 'below_50' not in res_dict['confidence']:  
                res_dict['below_50'] = [feat]
                res_dict['confidence']['below_50'] = label
            else:
                
                res_dict['confidence']['below_50'].extend(label)
                        
    return res_dict




## for removing ft from Length feature. Mignt not be needed if dictionary is applied
def char_2_dig(word):
    tmp_str = ""
    flag = 0
    for c in word:
        if c.isdigit():
            flag = 1
            tmp_str += c
    if flag:    
        return tmp_str
    return word