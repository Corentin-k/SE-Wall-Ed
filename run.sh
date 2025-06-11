# run.sh
#!/bin/bash
cd backend && python3 run.py &
cd frontend && npm run dev -- --host
