import os
from models import User, Document
from rag_system import process_document_for_rag

def seed_missing_roles():
    admin_user = User.get_user_by_username('admin')
    if not admin_user:
        print("No admin user found to attribute docs.")
        return

    hr_content = """# Global HR & Employee Leave Policies
## 1. Annual Leave Policy
All full-time employees are entitled to 20 days of paid annual leave per calendar year. Carrying forward a maximum of 5 days to the next year is permitted, subject to managerial approval.
## 2. Sick Leave and Medical Benefits
Employees receive 10 days of paid sick leave annually. For absences longer than 3 consecutive days, a registered medical certificate must be provided. Comprehensive health insurance, dental, and vision coverage are effective from the first day of employment.
## 3. Code of Conduct and Ethics
All employees must adhere to the highest standards of professional conduct. Harassment, discrimination, or any form of workplace bullying will result in immediate disciplinary action.
## 4. Maternity and Paternity Leave
Eligible employees receive 16 weeks of fully paid maternity leave and 4 weeks of fully paid paternity leave. Flexible return-to-work options are available.
"""

    clevel_content = """# Executive Board Strategy & Financial Performance Report
## 1. Top-Level Revenue Data
The company has exceeded its Q3 targets, achieving an aggregated revenue of $5.2 Billion globally, representing an 18% Year-Over-Year growth driven primarily by structural efficiencies.
## 2. Business Metrics & KPI Performance
Cost of Customer Acquisition (CAC) has decreased by 12% across North American markets. Lifetime Value (LTV) metrics have stabilized, resulting in an LTV:CAC ratio of 4.1.
## 3. Strategic Market Expansion
Executive priorities for Q4 include expanding the operational footprint into the Asia-Pacific region. Strategic partnerships are being finalized in Tokyo and Singapore to capture enterprise enterprise market share.
## 4. Risk Mitigation & Long Term Vision
Potential macroeconomic headwinds present moderate risks to operational cash flow. The board recommends a conservative hiring freeze for non-essential technical roles throughout the fourth quarter.
"""

    employee_content = """# Employee General Handbook & Workplace Behavior
## 1. Standard Workplace Hours
Core operational hours are between 9:00 AM and 5:00 PM local time. Employees are expected to be available for departmental meetings during this window. Flexible working arrangements must be approved by direct supervisors.
## 2. IT & Security Ethics Guidelines
Company-issued devices are strictly for professional use. Unauthorized installation of third-party software without IT approval is a violation of the cybersecurity protocol. Passwords must be updated every 60 days.
## 3. Office Behavior and Dress Code
The company promotes a 'business casual' dress code. Respectful behavior is mandatory in all physical and virtual environments, aligning with our inclusion initiatives.
## 4. Work From Home (WFH) Guidelines
Employees are eligible for 2 days of remote work per week under the hybrid model. A reliable internet connection and a secure, private working environment must be maintained on WFH days.
"""

    docs = [
        {'filename': 'hr_policies_and_benefits.md', 'content': hr_content, 'department': 'hr'},
        {'filename': 'executive_strategy_report.md', 'content': clevel_content, 'department': 'c-level'},
        {'filename': 'company_employee_handbook.md', 'content': employee_content, 'department': 'company_wide'}
    ]

    for d in docs:
        try:
            print(f"Uploading {d['filename']} for {d['department']}...")
            doc = Document.upload_document(
                filename=d['filename'],
                content=d['content'],
                file_type='md',
                uploaded_by_user_id=admin_user['_id'],
                department=d['department']
            )
            process_document_for_rag(doc['id'], d['content'], d['filename'])
        except Exception as e:
            print(f"Error processing {d['filename']}: {e}")
            
    print("Successfully trained missing roles!")

if __name__ == '__main__':
    seed_missing_roles()
