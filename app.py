from flask import Flask, request, jsonify, render_template, send_file, after_this_request
import sqlite3
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json['data']
    columns = [f"col_{i}" for i in range(len(data[0]))]
    rows = data

    # Создание временного файла базы данных с фиксированным именем
    db_path = os.path.join(tempfile.gettempdir(), 'database.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создание таблицы
    cursor.execute(f"CREATE TABLE IF NOT EXISTS mytable ({', '.join([f'{col} TEXT' for col in columns])})")

    # Очистка таблицы
    cursor.execute("DELETE FROM mytable")

    # Вставка данных
    cursor.executemany(f"INSERT INTO mytable ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in columns])})", rows)

    conn.commit()
    conn.close()

    return jsonify({"message": "Данные успешно сохранены", "file_url": f"/download/database.db"}), 200

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
        return response

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)