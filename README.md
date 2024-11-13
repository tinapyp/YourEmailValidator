To set up and run the project:

1. Backend Setup:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. Frontend Setup:

```bash
cd frontend
npm install
npm run dev
```

3. Create a `.env` file in the backend directory:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
```

4.Create a .env.local file in the frontend directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

This architecture provides:

1. Backend:

- Clean separation of concerns with modules for models, schemas, CRUD operations, and API endpoints
- Dependency injection for database sessions and current user
- Proper configuration management
- Type hints throughout the codebase

2. Frontend:

- Component-based architecture using React and Next.js
- Reusable UI components
- Type-safe with TypeScript
- Protected routes for authenticated users
- Clean separation of concerns between pages and components

The landing page has been integrated into the frontend and enhanced with:

- Authentication UI (login/register)
- Dashboard for managing API keys
- Responsive design
- Type-safe components

Would you like me to:

1. Add more frontend features like user profile management?
2. Implement the email validation endpoints?
3. Add documentation for the API endpoints?
4. Add tests for both frontend and backend?
