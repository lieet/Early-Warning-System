from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from requests import get
from json import loads
from joblib import load
import os

API_SERVER = os.environ.get('API_SERVER')
GET_USER = API_SERVER + '/user'
GET_CLASS = API_SERVER + '/class'
GET_GRADES = API_SERVER + '/grade'
GET_CLASS_GRADES = API_SERVER + '/class_grades'

app = Flask(__name__)
Bootstrap(app)

def get_model(week):
  modelName = 'lr_model_week{}.joblib'.format(week)
  return load(modelName)

def insert_warning_level(grades):
  pp = []
  pv = []
  for grade in grades:
    pp.append(grade['pp'])
    pv.append(grade['pv'])
    model = get_model(grade['week'])
    grade['warning_level'] = model.predict([pp+pv])

@app.route("/")
def homepage():
  user_response = get(GET_USER)
  user_data = user_response.text
  user = loads(user_data)
  class_response = get(GET_CLASS)
  class_data = class_response.text
  course = loads(class_data)
  if user['type'] == 'student':
    grades_response = get(GET_GRADES)
  else:
    grades_response = get(GET_CLASS_GRADES)
  grades_data = grades_response.text
  grades = loads(grades_data)
  if user['type'] == 'student':
    weeks = len(grades)
    insert_warning_level(grades)
  else:
    weeks = len(grades[0]['grades'])
    for class_grade in grades:
      insert_warning_level(class_grade['grades'])
  return render_template('index.html', title='Home page', user=user, course=course, grades=grades, weeks=weeks)

if __name__ == "__main__":
  if not API_SERVER:
    raise ValueError('You must have "SECRET_KEY" variable')
  app.run(debug=True)