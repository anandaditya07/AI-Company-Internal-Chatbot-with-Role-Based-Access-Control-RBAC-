# User Access Guide & Testing Scenarios

Use this guide to test the chatbot with different user roles. Each role has access to specific documents and will effectively "see" different answers based on their permissions.

## 🔑 User Credentials (Login Details)

| Role | Username (Email) | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Finance** | `finance_user@company.com` | `finance123` | Financial Reports, Summaries |
| **Marketing** | `marketing_user@company.com` | `marketing123` | Marketing Data, Campaign Reports |
| **HR** | `hr_user@company.com` | `hr123` | Employee Data, HR CSVs |
| **Engineering** | `engineering_user@company.com` | `engineering123` | Technical Documentation, Master Docs |
| **General** | `general_user@company.com` | `general123` | General Access (Note: Verify document mapping) |

---

## 🧪 Testing Questions per Role

Copy and paste these questions to verify that the **Retrieval-Augmented Generation (RAG)** and **Role-Based Access Control (RBAC)** are working correctly.

### 💰 Finance User
**Context:** Has access to `financial_summary.md` and `quarterly_financial_report.md`.

*   **Q1:** "What was the total revenue for the last quarter?"
*   **Q2:** "Summarize the key financial risks identified in the report."
*   **Q3:** "How did the operating expenses change compared to last year?"
*   **Q4:** "What is the projected budget for Q1 2025?"

### 📢 Marketing User
**Context:** Has access to `market_report_q4_2024.md`, `marketing_report_2024.md`, etc.

*   **Q1:** "What was the ROI for digital campaigns in 2024?"
*   **Q2:** "Which social media channel performed the best in Q3?"
*   **Q3:** "Summarize the marketing strategy for the upcoming product launch."
*   **Q4:** "What were the key customer feedback points regarding the new ad campaign?"

### 👥 HR User
**Context:** Has access to `hr_data.csv`.

*   **Q1:** "How many employees are currently in the Engineering department?"
*   **Q2:** "List the employees who joined in 2024."
*   **Q3:** "What is the average tenure of employees in the Sales team?"
*   **Q4:** "Who is the manager of the Marketing department?"

### ⚙️ Engineering User
**Context:** Has access to `engineering_master_doc.md`.

*   **Q1:** "What is the current architecture of the backend system?"
*   **Q2:** "List the deprecated API endpoints mentioned in the documentation."
*   **Q3:** "What are the coding standards for Python microservices?"
*   **Q4:** "Explain the deployment process for the production environment."

### 🛡️ Access Control Test (Negative Testing)
*Try asking these questions with the WRONG user to confirm they CANNOT see the data.*

*   **Log in as Marketing User** and ask: *"What is the engineering system architecture?"* -> **Result:** Should return "No relevant documents found" or a generic answer, NOT the sensitive info.
*   **Log in as HR User** and ask: *"What are the Q4 financial revenue targets?"* -> **Result:** Should not retrieve financial documents.
