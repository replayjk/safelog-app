import sqlite3
import os

def init_db():
    db_file = "reports.db"

    # 데이터베이스 파일이 없는 경우에만 초기화
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                image_path TEXT,
                timestamp TEXT,
                pdf_path TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("데이터베이스 초기화 완료")
    else:
        print("데이터베이스가 이미 존재합니다.")

init_db()
