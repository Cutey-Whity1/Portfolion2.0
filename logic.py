import json

    #Перевести json в словарь
def open_json(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # читает JSON из файла и преобразует в словарь
        return data
    
    #Перевести словарь в json
def update_json(json_path, data):
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)  # записываем данные в файл


def new_project(dict, name, desc, irl, skill_id, status_id):
    NP = dict["Projects"]["Example"]
    if dict["Projects"]["Project_list"]:  # Если список не пуст
        last_key = len(dict["Projects"]["Project_list"]) - 1
    else:
        last_key = 0

    NP['id'] = last_key
    NP["desc"] = desc
    NP["irl"] = irl
    NP["skill_id"] = skill_id
    NP["status_id"] = status_id
    dict["Projects"]["Project_list"][name] = NP
    dict["Projects"]["Example"] = {
      "id": 0,
      "user": "Cutey-Whity1",
      "desc": "example",
      "irl": "https:/your/irl/here",
      "skill_id": [],
      "status_id": 0
    }

def clear_projects(dict):
    dict["Projects"]["Project_list"] = {}

def delete_project(dict, project):
    del dict["Project"]["Project_list"][project]

def GPStatus(dict, project):
    dict["Projects"]["Project_list"][project]["status_id"]

def GPSkill(dict, project):
    dict["Projects"]["Project_list"][project]["skill_id"]
