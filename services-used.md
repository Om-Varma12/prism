## Catalyst services we have used

| # | Service | What we use it for |
|---|---|---|
| 2 | **AppSail (Docker/OCI)** | Our FastAPI backend + multi-agent system as a Docker container. This is the core — full control over Python, NetworkX, ChromaDB, Groq calls |
| 4 | **Slate or Web Client Hosting** | React + Vite frontend |
| 5 | **Domain Mappings** | Custom domain + SSL for the demo URL |
| 6 | **Data Store** | The actual crime DB — CaseMaster, Accused, Victim, etc. (relational, matches the given schema exactly) |
| 8 | **Stratus** | Store generated PDFs (conversation exports), case attachment placeholders |
| 9 | **Cache** | Cache frequent queries — district stats, dashboard KPIs — avoid recomputation |
| 17 | **Authentication** | Login + role-based access (Investigator/Analyst/Supervisor) |
| 18 | **API Gateway** | Sits in front of our AppSail backend — routing, auth, throttling |
| 20 | **Cron (Cloud Scale)** | Daily job: emerging crime cluster detection, alert generation, forecast refresh |
| 21 | **Signals + Event Functions** | Trigger alert generation when new FIR-like data is inserted (simulates real-time intelligence) |
| 26 | **Pipelines** | CI/CD — deploy on push, judges see clean DevOps story |