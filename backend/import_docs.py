import os
from models import User, Document
from rag_system import process_document_for_rag

def import_all_docs():
    # Find admin user
    admin_user = User.get_user_by_username('admin')
    if not admin_user:
        admins = User.get_users_by_role('admin')
        if admins:
            admin_user = admins[0]
        else:
            print("No admin user found to attribute docs.")
            return

    base_dir = r"d:\python\company-chatbot-rbac\backend\fintech_data"
    departments_map = {
        'Finance': 'finance',
        'HR': 'hr',
        'engineering': 'engineering',
        'general': '',
        'marketing': 'marketing'
    }

    count = 0
    for dir_name, dept in departments_map.items():
        dept_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dept_path):
            for filename in os.listdir(dept_path):
                if filename.endswith('.md') or filename.endswith('.txt'):
                    file_path = os.path.join(dept_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        print(f"Uploading {filename} for {dept}...")
                        doc = Document.upload_document(
                            filename=filename,
                            content=content,
                            file_type=filename.split('.')[-1],
                            uploaded_by_user_id=admin_user['_id'],
                            department=dept
                        )
                        
                        process_document_for_rag(doc['id'], content, filename)
                        count += 1
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                    
    print(f"Successfully processed {count} documents!")

if __name__ == '__main__':
    import_all_docs()
