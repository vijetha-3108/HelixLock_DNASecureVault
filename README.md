# HelixLock_DNASecureVault
# 🔐 HelixLock: DNA Secure Vault

A bio-inspired secure data vault that leverages DNA-based encoding techniques to protect sensitive information. Built with a focus on **security, scalability, and real-world application design**.

---

## 🚀 Overview

HelixLock explores an unconventional approach to data security by combining **DNA sequence logic (A, T, C, G)** with modern web technologies. The system allows users to securely store, encrypt, and manage sensitive data through a structured vault interface.

---

## ⚙️ Features

* 🧬 DNA-based encryption & decryption
* 🔐 Token-based authentication system
* 📁 Secure vault for storing sensitive entries
* 📜 Activity logging for tracking user actions
* 🛡️ Browser autofill mitigation in login forms
* 🎨 Clean and responsive UI
* 🧩 Modular Flask backend (routes → services → models)

---

## 🛡️ Security Highlights

### 🔒 Autofill Mitigation (Advanced)

Browsers often store and auto-suggest credentials, which can expose sensitive data.

HelixLock implements:

* Disabled unwanted autofill behavior
* Controlled input handling
* Reduced credential persistence risks

This adds a **practical security layer** often overlooked in standard applications.

---

## 🧠 Tech Stack

**Frontend:** HTML, CSS, JavaScript
**Backend:** Python, Flask
**Database:** MongoDB / CSV (configurable)

---

## 📂 Project Structure

```
backend/
 ├── routes/
 ├── services/
 ├── models/
 ├── utils/

frontend/
 ├── html/
 ├── css/
 ├── js/
```

---

## ▶️ How to Run

### 1. Clone the repository

```
git clone https://github.com/your-username/helixlock-dna-vault.git
cd helixlock-dna-vault
```

### 2. Setup virtual environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run backend

```
python run.py
```

Backend runs at:

```
http://127.0.0.1:5000
```

### 5. Run frontend

Use Live Server OR open index.html:

```
http://127.0.0.1:5500
```

---

## 🧪 Sample Input

```
Chemical name: Sodium Chloride
Formula: NaCl
Notes: Highly sensitive lab sample – restricted access
Encryption key: ATCGTACGGA
```

---

## 📈 Future Improvements

* JWT Authentication with RBAC
* Password hashing & validation
* Advanced encryption logic
* Cloud deployment (AWS / Render)
* Anomaly detection system

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork and improve.

---

## 📬 Feedback

If you have suggestions or improvements, feel free to open an issue or connect.

---

## ⭐ Show Your Support

If you found this project interesting, consider giving it a ⭐ on GitHub!
