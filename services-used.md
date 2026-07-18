## Catalyst services we have used

| # | Service | What we use it for |
|---|---|---|
| 1 | **AppSail (Docker)** | Our FastAPI backend + multi-agent system as a Docker container. This is the core — full control over Python, NetworkX, ChromaDB, Groq calls |
| 2 | **Slate** | React + Vite frontend |
| 3 | **Data Store** | The actual crime DB — CaseMaster, Accused, Victim, etc. (relational, matches the given schema exactly) |
| 4 | **Stratus** | Store generated PDFs (conversation exports), case attachment placeholders |
| 5 | **Cache** | Cache frequent queries — district stats, dashboard KPIs — avoid recomputation |
| 6 | **Authentication** | Login & Sign-up |