from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os
import traceback

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SECRET_KEY'] = 'AIzaSyDmIxrIJh2Zb7Ae97sFpu2GJnbUp0sPQak'
db = SQLAlchemy(app)

# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    family_income = db.Column(db.String(50), nullable=False)
    parent_occupation = db.Column(db.String(100), nullable=False)
    digital_access = db.Column(db.String(10), nullable=False)
    distance = db.Column(db.Float, nullable=False)
    results_percentage = db.Column(db.Float, nullable=False)

# Replace with your actual Gemini API key
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY'  # Replace this with your real key
genai.configure(api_key=GEMINI_API_KEY)

def predict_financial_aid(student):
    """Use Gemini AI to predict financial aid eligibility with error handling."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = f"Student details: Class {student['student_class']}, Family Income: {student['family_income']}, Parent Occupation: {student['parent_occupation']}, Digital Access: {student['digital_access']}, Distance: {student['distance']}km, Results: {student['results_percentage']}%. Provide a concise risk assessment: Alert, High Risk, Risky. Suggest what can be done."
        response = model.generate_content(prompt)
        return response.text if response else "Gemini response was empty."
    except Exception as e:
        print(f"Error in predict_financial_aid: {e}")
        print(traceback.format_exc())
        return f"Error during Gemini prediction: {e}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict/<int:student_id>')
def predict(student_id):
    student = Student.query.get_or_404(student_id)
    student_data = {
        "name": student.name,
        "student_class": student.student_class,
        "family_income": student.family_income,
        "parent_occupation": student.parent_occupation,
        "digital_access": student.digital_access,
        "distance": student.distance,
        "results_percentage": student.results_percentage
    }
    print("Student Data for Prediction (ID):", student_data)  # Debugging print
    prediction = predict_financial_aid(student_data)
    print("Prediction Result (ID):", prediction)  # Debugging print
    return render_template('prediction.html', student=student, prediction=prediction)

@app.route('/predict_manual', methods=['POST'])
def predict_manual():
    student_data = {
        "name": request.form['name'],
        "student_class": request.form['student_class'],
        "family_income": request.form['family_income'],
        "parent_occupation": request.form['parent_occupation'],
        "digital_access": request.form['digital_access'],
        "distance": request.form['distance'],
        "results_percentage": request.form['results_percentage']
    }
    print("Student Data for Prediction (Manual):", student_data)  # Debugging print
    prediction = predict_financial_aid(student_data)
    print("Prediction Result (Manual):", prediction)  # Debugging print
    return render_template('prediction.html', student=student_data, prediction=prediction)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures database tables are created inside the application context
    app.run(debug=True)
