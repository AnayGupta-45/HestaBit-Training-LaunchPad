from collections import defaultdict

sessions = defaultdict(list)

def add_message(session_id, role, content):
    sessions[session_id].append({"role": role, "content": content})

def get_history(session_id):
    return sessions[session_id]

def clear_session(session_id):
    sessions[session_id] = []