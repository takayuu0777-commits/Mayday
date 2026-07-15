import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from modules.database import connect


def normalize_email(email):
    return (email or "").strip().lower()


def create_user(name, email, password):
    clean_name = (name or "").strip()
    clean_email = normalize_email(email)
    clean_password = password or ""

    if not clean_name:
        return {
            "success": False,
            "message": "名前を入力してください。"
        }

    if not clean_email or "@" not in clean_email:
        return {
            "success": False,
            "message": "正しいメールアドレスを入力してください。"
        }

    if len(clean_password) < 8:
        return {
            "success": False,
            "message": "パスワードは8文字以上にしてください。"
        }

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT id
    FROM users
    WHERE email = ?
    """, (clean_email,))

    existing_user = c.fetchone()

    if existing_user:
        conn.close()

        return {
            "success": False,
            "message": "このメールアドレスは既に登録されています。"
        }

    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    c.execute("""
    INSERT INTO users
    (
        id,
        name,
        email,
        password_hash,
        created_at,
        is_active
    )
    VALUES (?, ?, ?, ?, ?, 1)
    """, (
        user_id,
        clean_name,
        clean_email,
        generate_password_hash(clean_password),
        now
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "user_id": user_id,
        "message": "アカウントを作成しました。"
    }


def authenticate_user(email, password):
    clean_email = normalize_email(email)
    clean_password = password or ""

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT *
    FROM users
    WHERE email = ?
      AND is_active = 1
    """, (clean_email,))

    user = c.fetchone()
    conn.close()

    if not user:
        return {
            "success": False,
            "message": "メールアドレスまたはパスワードが違います。"
        }

    if not check_password_hash(
        user["password_hash"],
        clean_password
    ):
        return {
            "success": False,
            "message": "メールアドレスまたはパスワードが違います。"
        }

    return {
        "success": True,
        "user": dict(user)
    }


def get_user(user_id):
    if not user_id:
        return None

    conn = connect()
    c = conn.cursor()

    c.execute("""
    SELECT
        id,
        name,
        email,
        created_at,
        is_active
    FROM users
    WHERE id = ?
      AND is_active = 1
    """, (user_id,))

    user = c.fetchone()
    conn.close()

    if not user:
        return None

    return dict(user)