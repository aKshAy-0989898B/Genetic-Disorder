## Genetic Disorder Detection Web App

This project is a Flask web application that uses a fine-tuned DNABERT model to predict likely genetic disorders from genomic DNA sequences. Predictions and patient metadata are stored in a local SQLite database.

The app supports:
- Manual sequence input with basic patient details
- Uploading text files containing FASTA-like genomic sequences
- Viewing a history of all past predictions

The main application entry point is [app.py](file:///c:/Users/Akshay%20V/OneDrive/Desktop/Genetic%20Disorder/webapp/app.py) inside the `webapp` folder.

---

## 1. Prerequisites

- **Python**: 3.10 or later
- **Operating system**: Windows (tested), but any OS with Python should work
- **Python packages**:
  - `flask`
  - `transformers`
  - `torch`
   - `sqlite3`
  - `pandas`
  - `huggingface_hub` (installed automatically with `transformers`)

You also need the following local files and folders in `webapp/`:

- `dnabert_finetuned/`
  - `config.json`
  - `model.safetensors`
  - `tokenizer_config.json`
  - `special_tokens_map.json`
  - `vocab.txt`
- `tokenized_genome_data.csv`
- `templates/`
  - `home.html`
  - `input_page.html`
  - `upload_page.html`
  - `history.html`

These are already present in the project.

---

## 2. Environment Setup

From the project root:

```bash
cd "C:\Users\Akshay V\OneDrive\Desktop\Genetic Disorder"
```

Optionally create and activate a virtual environment (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install required packages:

```bash
pip install flask transformers torch pandas
```

If PyTorch installation fails, follow the instructions at https://pytorch.org for your OS and hardware.

---

## 3. How to Run the App

From the project root directory:

```bash
cd "C:\Users\Akshay V\OneDrive\Desktop\Genetic Disorder"
python webapp\app.py
```

If everything is set up correctly, you should see output similar to:

```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open a browser and navigate to:

```text
http://127.0.0.1:5000
```

This will load the home page of the web app.

---

## 4. App Pages and Usage

### 4.1 Home Page (`/`)

- Landing page with navigation links to:
  - **Input sequence**
  - **Upload file**
  - **Prediction history**

### 4.2 Manual Input (`/input`)

This page lets you enter a single DNA sequence and basic patient details.

Fields:
- `Name` (text; required)
- `Age` (integer; required)
- `Sex` (select: `male`, `female`, or `other`; required)
- `Chronic illnesses` (free text; optional)
- `Symptoms` (free text; optional)
- `Genomic sequence` (required)

The genomic sequence should be a string consisting of nucleotide characters:

```text
ACGTACGTGACCTGACTGACTGACCTGACCGT...
```

After submitting:
- The DNABERT model predicts the most likely disorder.
- A confidence score (percentage) is displayed.
- The input and prediction are saved into the local SQLite database `predictions.db`.

### 4.3 File Upload (`/upload`)

This page accepts a `.txt` file containing one or more genomic sequences. The expected format is FASTA-like:

- Lines starting with `>` are treated as headers.
- Subsequent lines until the next `>` are concatenated to form one DNA sequence.

Example file content:

```text
>sample_1
ACGTACGTGACCTGACTGACTGACCTGACCGT
ACGTACGTGACCTGACTGACTGACCTGACCGT
>sample_2
GTCAGTCAGTCAGTCAGTCAGTCAAGTCAGTC
```

Steps:
1. Click **Choose File** and select a `.txt` file.
2. Click **Upload**.
3. The app processes each sequence and shows a table with:
   - Truncated sequence (first ~50 characters)
   - Predicted disorder
   - Confidence score

### 4.4 Prediction History (`/history`)

- Displays all past predictions stored in `predictions.db`.
- Each entry includes:
  - Name, age, sex
  - Original sequence (or truncated)
  - Predicted disorder
  - Confidence score

---

## 5. Sample Inputs

### 5.1 Manual Input Example

Use the `/input` page and fill in:

- Name: `John Doe`
- Age: `35`
- Sex: `male`
- Chronic illnesses: `hypertension`
- Symptoms: `chest pain, fatigue`
- Genomic sequence:

```text
ACGTACGTGACCTGACTGACTGACCTGACCGTACGTACGTGACCTGACTGACTGACCTGACCGT
```

Click **Submit**. 

### 5.2 Upload File Example

Create a file `sample_sequence.txt` with:

```text
>patient_1
ACGTACGTGACCTGACTGACTGACCTGACCGTACGTACGTGACCTGACTGACTGACCTGACCGT
>patient_2
GTCAGTCAGTCAGTCAGTCAGTCAAGTCAGTCGTCAGTCAGTCAGTCAGTCAGTCAAGTCAGTC
```

Then:

1. Go to `/upload`.
2. Select `sample_sequence.txt`.
3. Click **Upload** to see predictions for both sequences.

---

## 6. Troubleshooting

- **401 Unauthorized from huggingface.co**  
  The app is configured to run in offline mode and load DNABERT from the local `dnabert_finetuned` folder. If you still see 401 errors, ensure:
  - All model files are present inside `webapp/dnabert_finetuned/`.
  - You are running the updated `app.py` with `local_files_only=True` and offline environment variables set.

- **FileNotFoundError for `tokenized_genome_data.csv`**  
  Ensure that `tokenized_genome_data.csv` is located in:
  - `webapp/tokenized_genome_data.csv`

- **Port already in use**  
  If another process is using port `5000`, either:
  - Stop the other process, or
  - Modify `app.run(debug=True)` in `app.py` to use a different port:
    - `app.run(debug=True, port=5001)`

---

## 7. Notes

- This app is intended for educational and experimental purposes only. It is **not** a medical device and its predictions must not be used for clinical decision making.

