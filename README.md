

# Mini Compliance Tracker Live Deployed Link:
https://mini-compliance-tracker-8lyh.onrender.com

# Mini Compliance Tracker - LedgersCFO

A full-stack web application designed for CFO teams to manage multi-client compliance tasks, track deadlines, and visualize overdue filings.

## Features
- **Client Management**: Quick navigation through different companies.
- **Task Tracking**: View, add, and update compliance tasks (GST, ROC, Income Tax).
- **Overdue Highlighting**: Automatic red-flagging of pending tasks past their due date.
- **Summary Dashboard**: Real-time counts of total, pending, and overdue tasks.
- **Persistent Storage**: Uses SQLite to ensure data remains consistent.

## Tech Stack
- **Backend**: Python (Flask)
- **Database**: SQLAlchemy (SQLite)
- **Frontend**: Vanilla JS (ES6+), Bootstrap 5, HTML5/CSS3
- **Deployment**: Ngrok for secure tunneling

## Design Decisions & Tradeoffs
1. **Single Page Application (SPA) Approach**: I chose a vanilla JS SPA architecture to provide a snappy user experience without the overhead of React/Vue for a "Mini" project.
2. **SQLite**: Used for persistence over in-memory arrays to demonstrate production-like data handling.
3. **Overdue Logic**: Calculated dynamically on the frontend to ensure the UI stays updated relative to the user's local clock.

