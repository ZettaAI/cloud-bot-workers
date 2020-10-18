from google.cloud import firestore


db = firestore.Client()


def is_admin(user_id: str) -> bool:
    doc_ref = db.collection("admins").document(user_id)
    return doc_ref.get().exists

