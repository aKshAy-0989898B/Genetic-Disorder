import os
import torch
import torch.nn.functional as F
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd

app = Flask(__name__)
app.secret_key = 'ak@11'

MODEL_PATH = "dnabert_finetuned"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

df = pd.read_csv("tokenized_genome_data.csv")
label_encoder = {i: label for i, label in enumerate(df["Disorder"].unique())}

def init_db():
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    sex TEXT,
                    chronic_illnesses TEXT,
                    symptoms TEXT,
                    sequence TEXT,
                    disorder TEXT,
                    confidence REAL)''')
    conn.commit()
    conn.close()

init_db()

def kmer_tokenizer(sequence, k=6):
    return " ".join([sequence[i:i+k] for i in range(len(sequence) - k + 1)])

def predict_disorder(sequence, name="NA", age="NA", sex="NA", chronic_illnesses="NA", symptoms="NA"):
    tokenized_seq = kmer_tokenizer(sequence, k=6)
    inputs = tokenizer(tokenized_seq, return_tensors="pt", truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = F.softmax(outputs.logits, dim=1).squeeze().tolist()
    predicted_label_index = torch.argmax(outputs.logits, dim=1).item()
    confidence_score = probabilities[predicted_label_index] * 100
    predicted_disorder = label_encoder.get(predicted_label_index, "Unknown Disorder")

    save_prediction(sequence, predicted_disorder, confidence_score, name, age, sex, chronic_illnesses, symptoms)
    return predicted_disorder, confidence_score

def save_prediction(sequence, disorder, confidence, name, age, sex, chronic_illnesses, symptoms):
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute('''INSERT INTO predictions 
                (name, age, sex, chronic_illnesses, symptoms, sequence, disorder, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
             (name, age, sex, chronic_illnesses, symptoms, sequence, disorder, confidence))
    conn.commit()
    conn.close()

def process_genome_file(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    results = []
    current_sequence = ""
    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            if current_sequence:
                disorder, confidence = predict_disorder(current_sequence)
                results.append((current_sequence[:50] + "...", disorder, confidence))
            current_sequence = ""
        else:
            current_sequence += line

    if current_sequence:
        disorder, confidence = predict_disorder(current_sequence)
        results.append((current_sequence[:50] + "...", disorder, confidence))

    return results

def get_prediction_history():
    conn = sqlite3.connect('predictions.db')
    c = conn.cursor()
    c.execute("SELECT name, age, sex, sequence, disorder, confidence FROM predictions ORDER BY id DESC")
    history = c.fetchall()
    conn.close()
    return history

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/input", methods=["GET", "POST"])
def input_sequence():
    prediction_result = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        sex = request.form.get("sex", "").strip()
        chronic_illnesses = request.form.get("chronic_illnesses", "").strip()
        symptoms = request.form.get("symptoms", "").strip()
        user_sequence = request.form.get("user_input", "").strip()

        if not name or not age.isdigit() or sex not in ['male', 'female', 'other'] or not user_sequence:
            flash("All fields must be filled correctly", "danger")
            return redirect(request.url)

        disorder, confidence = predict_disorder(
            user_sequence,
            name=name,
            age=age,
            sex=sex,
            chronic_illnesses=chronic_illnesses,
            symptoms=symptoms
        )
        prediction_result = (name, age, sex, user_sequence[:50] + "...", disorder, confidence)

    return render_template("input_page.html", prediction_result=prediction_result)

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    file_results = None
    if request.method == "POST":
        if "genome_file" in request.files:
            file = request.files["genome_file"]
            if file.filename == '' or not file.filename.lower().endswith('.txt'):
                flash("Please upload a valid .txt file", "danger")
                return redirect(request.url)
            file_path = os.path.join("uploads", file.filename)
            file.save(file_path)
            file_results = process_genome_file(file_path)
            flash("File processed successfully", "success")

    return render_template("upload_page.html", file_results=file_results)

@app.route("/history")
def history():
    history = get_prediction_history()
    return render_template("history.html", history=history)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
