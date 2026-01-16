# Task Manager Application

A modern task management application built with React and Django.

## Features

- User authentication with JWT tokens
- Create, read, update, and delete tasks
- Real-time task updates
- Responsive design
- Auto-refresh token mechanism

## Setup

### Prerequisites

- Node.js 14+
- npm or yarn

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=https://todo-manager-api-ux4e.onrender.com
```

### Development

```bash
npm start
```

The app runs on `http://localhost:3000`

### Production Build

```bash
npm run build
```

## Deployment on Vercel

1. Push to GitHub
2. Connect repository to Vercel
3. Set environment variable: `REACT_APP_API_URL=https://todo-manager-api-ux4e.onrender.com`
4. Deploy

## API Endpoints

- **POST** `/api/token/` - Get JWT tokens
- **POST** `/api/auth/register/` - Register new user
- **GET** `/api/auth/me/` - Get current user
- **GET** `/api/tasks/` - Get all tasks
- **POST** `/api/tasks/` - Create task
- **PUT** `/api/tasks/{id}/` - Update task
- **DELETE** `/api/tasks/{id}/` - Delete task

## Architecture

```
src/
├── components/
│   ├── LoginForm.js
│   ├── TaskList.js
│   ├── TaskForm.js
│   └── TaskItem.js
├── api/
│   └── tasks.js
├── App.js
└── index.js
```

## Technologies

- React 18
- Axios
- Tailwind CSS
- Django (Backend)

## License

MIT
