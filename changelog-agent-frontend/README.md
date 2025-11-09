# Form Builder Agent - Frontend

React + TypeScript frontend for the changelog agent backend.

## Quick Start

### Prerequisites
- Node.js 18+
- Backend running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Start Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:5173` (or the next available port).

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Testing the Application

1. **Start the backend** (in a separate terminal):
   ```bash
   cd ../changelog-agent-backend
   docker compose up
   ```

2. **Start the frontend**:
   ```bash
   npm run dev
   ```

3. **Open in browser**: Navigate to the URL shown in terminal (usually `http://localhost:5173`)

4. **Test features**:
   - Click "+ New Conversation" to create a conversation
   - Type a message like "Add Paris option to travel form"
   - Click Send and watch the agent respond
   - Expand "Tool Calls" at the bottom to see what the agent did
   - Click on another conversation to switch between them
   - Delete conversations with the × button

## Project Structure

```
src/
├── api/
│   └── client.ts              # Backend API client
├── components/
│   ├── ConversationList.tsx   # Sidebar with conversations
│   ├── ChatInterface.tsx      # Main chat area
│   ├── MessageBubble.tsx      # Individual message display
│   └── ToolCallPanel.tsx      # Tool calls inspector
├── types/
│   └── index.ts               # TypeScript definitions
├── App.tsx                    # Main application
├── main.tsx                   # Entry point
└── index.css                  # Tailwind directives
```

## Tech Stack

- React 18
- TypeScript
- Vite
- TailwindCSS

## Features

- Create and manage multiple conversations
- Real-time chat interface with the agent
- View conversation history
- Inspect tool calls (what the agent did)
- Delete conversations
- Auto-scroll to latest message
- Loading states and error handling

See `README_PROJECT.md` for detailed architecture documentation.
