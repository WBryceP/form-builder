import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional
from agents import SQLiteSession


class ConversationService:
    def __init__(self, sessions_db: str):
        self.sessions_db = sessions_db
        self._init_metadata_table()
    
    def _init_metadata_table(self):
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    trace_id TEXT
                )
            """)
            
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'trace_id' not in columns:
                cursor.execute("ALTER TABLE conversations ADD COLUMN trace_id TEXT")
            
            conn.commit()
    
    def create_conversation(self, title: str = "New Conversation") -> dict:
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, title, created_at, updated_at, message_count)
                VALUES (?, ?, ?, ?, 0)
            """, (session_id, title, created_at, created_at))
            conn.commit()
        
        return {
            "session_id": session_id,
            "title": title,
            "created_at": created_at
        }
    
    def list_conversations(self) -> list[dict]:
        with sqlite3.connect(self.sessions_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, title, created_at, updated_at, message_count
                FROM conversations
                ORDER BY updated_at DESC
            """)
            rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_conversation(self, session_id: str) -> Optional[dict]:
        with sqlite3.connect(self.sessions_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, title, created_at, updated_at, message_count
                FROM conversations
                WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def update_conversation_metadata(self, session_id: str, title: Optional[str] = None):
        updated_at = datetime.utcnow().isoformat() + "Z"
        
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            
            if title:
                cursor.execute("""
                    UPDATE conversations
                    SET updated_at = ?, title = ?, message_count = message_count + 1
                    WHERE session_id = ?
                """, (updated_at, title, session_id))
            else:
                cursor.execute("""
                    UPDATE conversations
                    SET updated_at = ?, message_count = message_count + 1
                    WHERE session_id = ?
                """, (updated_at, session_id))
            
            conn.commit()
    
    def ensure_conversation_exists(self, session_id: str, title: str = "New Conversation"):
        existing = self.get_conversation(session_id)
        if not existing:
            created_at = datetime.utcnow().isoformat() + "Z"
            with sqlite3.connect(self.sessions_db) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (session_id, title, created_at, updated_at, message_count)
                    VALUES (?, ?, ?, ?, 0)
                """, (session_id, title, created_at, created_at))
                conn.commit()
    
    def delete_conversation(self, session_id: str) -> bool:
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
        
        if deleted:
            try:
                session = SQLiteSession(session_id, self.sessions_db)
                session.clear()
            except Exception:
                pass
        
        return deleted
    
    def get_conversation_messages(self, session_id: str) -> list[dict]:
        try:
            with sqlite3.connect(self.sessions_db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT message_data, created_at
                    FROM agent_messages
                    WHERE session_id = ?
                    ORDER BY created_at ASC
                """, (session_id,))
                rows = cursor.fetchall()
            
            messages = []
            for row in rows:
                try:
                    data = json.loads(row['message_data'])
                    
                    if 'role' in data and data['role'] in ['user', 'assistant']:
                        content = data.get('content', '')
                        
                        if data['role'] == 'assistant':
                            if isinstance(content, list) and len(content) > 0:
                                if isinstance(content[0], dict) and 'text' in content[0]:
                                    content = content[0]['text']
                            elif isinstance(content, str):
                                try:
                                    content_list = json.loads(content)
                                    if isinstance(content_list, list) and len(content_list) > 0:
                                        if 'text' in content_list[0]:
                                            content = content_list[0]['text']
                                except (json.JSONDecodeError, KeyError, IndexError):
                                    pass
                        
                        if not isinstance(content, str):
                            content = json.dumps(content)
                        
                        messages.append({
                            "role": data['role'],
                            "content": content,
                            "timestamp": row['created_at'] if row['created_at'] else datetime.utcnow().isoformat() + "Z"
                        })
                except json.JSONDecodeError:
                    continue
            
            return messages
        except Exception:
            return []
    
    def set_trace_id(self, session_id: str, trace_id: str):
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE conversations
                SET trace_id = ?
                WHERE session_id = ?
            """, (trace_id, session_id))
            conn.commit()
    
    def get_trace_id(self, session_id: str) -> Optional[str]:
        with sqlite3.connect(self.sessions_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trace_id
                FROM conversations
                WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
        
        return row[0] if row and row[0] else None
