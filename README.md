# Kochi Metro Rail Document Hub 📝

**Kochi Metro Rail Document Hub** is a web-based application designed to help different departments within Kochi Metro Rail Limited (KMRL) manage and search internal documents more efficiently. This tool allows users to upload plain text files, which are then processed and indexed for a fast and intelligent search experience.

### **Core Features**

* **Secure User Authentication:** The application uses Flask-Login to provide a secure login system with predefined user roles for different departments, such as Engineering, Financial, and Admin.
* **Intelligent Document Processing:** When a user uploads a `.txt` file, the application automatically extracts key metadata such as the title, vendor, and category. It also analyzes the content using **spaCy**, a powerful NLP library, to enable sophisticated searches. 
* **Smart Search Functionality:** The search bar allows users to query documents using natural language. The system ranks results based on a hybrid scoring model that combines keyword matching with semantic similarity, ensuring the most relevant documents are displayed first. 
* **Role-Based Access Control:** Users can only view and search for documents uploaded by their own department, ensuring data privacy and security. The "Admin" role has access to all documents.
* **In-App Document Viewer:** Users can click on a search result to view the document's content directly within a modal, without needing to download the file.
* **Simple and Clean UI:** The front-end is built with **Tailwind CSS** to provide a modern, responsive, and easy-to-use interface.

---

### **Technical Stack** 💻

* **Backend:** **Python** with **Flask**.
* **NLP:** **spaCy** for natural language processing and semantic analysis.
* **Frontend:** **HTML**, **JavaScript**, and **Tailwind CSS**.
* **Dependencies:** `Flask`, `Flask-Login`, `spaCy`, `en_core_web_md`.

---

### **Setup and Installation** 🛠️

To get the application up and running on your local machine, follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone [your-repository-url]
    cd [your-project-directory]
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Required Libraries**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You'll need to create a `requirements.txt` file by running `pip freeze > requirements.txt` after installing the dependencies listed in `app.py`.)*

4.  **Run the Flask Application**
    ```bash
    python app.py
    ```
    The application will run on `http://127.0.0.1:5001`.

---

### **Usage** 🧑‍💻

1.  **Login:** Use one of the predefined usernames to log in: `eng_user`, `fin_user`, or `admin`. There is no password required for this prototype.
2.  **Upload:** Use the "Upload Document" section to select a `.txt` file. The file will be processed and added to the database.
3.  **Search:** Use the search bar to query for documents. The search can be done by content, title, category, or date.
4.  **View & Download:** Click on a search result to view its content within a modal or click the download icon to save the file.

---

### **Contributing** 🤝

Contributions are welcome! If you have suggestions for new features, bug fixes, or improvements, please feel free to open an issue or submit a pull request.
