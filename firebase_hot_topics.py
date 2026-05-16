"""Firebase 热点数据同步模块 - 使用 Admin SDK"""
from pathlib import Path
import os
from datetime import datetime

# 禁用代理（尝试解决国内网络问题）
os.environ["NO_PROXY"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"
os.environ["no_proxy"] = "firestore.googleapis.com,googleapis.com,oauth2.googleapis.com"

FIREBASE_PROJECT_ID = "hottopic-7b5a7"
KEY_FILES = [
    Path(__file__).parent / "serviceAccountKey.json",
    Path(__file__).parent / "firebase_key.json",
    Path(__file__).parent / ".trae" / "rules" / "firebase-credentials.json",
]

# Firebase 状态标志
_firebase_available = None
_firebase_initialized = False


def _check_firebase_available():
    """检查 Firebase SDK 是否可用"""
    global _firebase_available
    if _firebase_available is not None:
        return _firebase_available
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        _firebase_available = True
        return True
    except ImportError as e:
        print(f"[Firebase] SDK 不可用: {e}")
        _firebase_available = False
        return False


def _get_app():
    """获取或初始化 Firebase App，失败返回 None。"""
    global _firebase_initialized
    
    if not _check_firebase_available():
        return None
    
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        # 如果已经初始化，直接返回
        if firebase_admin._apps:
            _firebase_initialized = True
            return firebase_admin.get_app()

        # 查找密钥文件
        key_file = None
        for f in KEY_FILES:
            if f.exists():
                key_file = str(f)
                break

        if not key_file:
            print("[Firebase] 未找到服务账号密钥文件，跳过")
            return None

        cred = credentials.Certificate(key_file)
        app = firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_PROJECT_ID,
        })
        _firebase_initialized = True
        print(f"[Firebase] 已初始化: {FIREBASE_PROJECT_ID}")
        return app
    except Exception as e:
        print(f"[Firebase] 初始化失败: {e}")
        _firebase_available = False
        return None


def _get_db():
    """获取 Firestore client，失败返回 None。"""
    app = _get_app()
    if not app:
        return None
    try:
        from firebase_admin import firestore
        return firestore.client(app=app)
    except Exception as e:
        print(f"[Firebase] Firestore client 失败: {e}")
        return None


def sync_to_firebase(hot_topics):
    """将热点列表同步到 Firestore (config/hot_topics)。"""
    db = _get_db()
    if not db:
        return
    try:
        from firebase_admin import firestore
        
        # 确保每个热点都有 display 字段（默认为 True）
        topics_with_display = []
        for topic in hot_topics:
            topic_copy = topic.copy()
            if 'display' not in topic_copy:
                topic_copy['display'] = True
            topics_with_display.append(topic_copy)
        
        doc_ref = db.collection("config").document("hot_topics")
        doc_ref.set({
            "topics": topics_with_display,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "sync_time": datetime.now().isoformat()
        })
        print(f"[Firebase] 同步成功 ({len(topics_with_display)} 个热点)")
    except Exception as e:
        print(f"[Firebase] 同步失败: {type(e).__name__}: {e}")


def sync_groups_to_firebase(groups):
    """将分组列表同步到 Firestore (config/groups)。"""
    db = _get_db()
    if not db:
        return
    try:
        from firebase_admin import firestore
        
        doc_ref = db.collection("config").document("groups")
        doc_ref.set({
            "groups": groups,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "sync_time": datetime.now().isoformat()
        })
        print(f"[Firebase] 分组同步成功 ({len(groups)} 个分组)")
    except Exception as e:
        print(f"[Firebase] 分组同步失败: {type(e).__name__}: {e}")


def load_from_firebase(include_hidden=False):
    """
    从 Firestore 加载热点列表，失败返回 None。
    
    Args:
        include_hidden: 是否包含 display=false 的热点，默认只返回 display=true 的热点
    """
    db = _get_db()
    if not db:
        return None
    try:
        doc_ref = db.collection("config").document("hot_topics")
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            topics = data.get("topics", [])
            
            # 过滤 display=false 的热点（除非明确要求包含）
            if not include_hidden:
                topics = [t for t in topics if t.get('display', True)]
            
            print(f"[Firebase] 加载成功 ({len(topics)} 个热点)")
            return topics
        else:
            print("[Firebase] 云端尚无数据")
            return None
    except Exception as e:
        print(f"[Firebase] 加载失败: {type(e).__name__}: {e}")
        return None
