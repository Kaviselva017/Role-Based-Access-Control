from pymongo import MongoClient

def fix_departments():
    db = MongoClient('mongodb://localhost:27017')['company_chatbot_rbac']
    db['documents'].update_many({'department': 'c-level'}, {'$set': {'department': 'Executive'}})
    db['documents'].update_many({'department': 'hr'}, {'$set': {'department': 'Human Resources'}})
    db['documents'].update_many({'department': 'company_wide'}, {'$set': {'department': 'General'}})
    db['documents'].update_many({'department': ''}, {'$set': {'department': 'General'}})
    print("Done")

if __name__ == '__main__':
    fix_departments()
