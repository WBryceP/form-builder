# Form Builder Agent - Frontend

A React + TypeScript frontend for the changelog agent backend.

## Project Structure

```
src/
├── api/
│   └── client.ts           # API client for backend communication
├── components/
│   ├── ConversationList.tsx    # Sidebar with conversation list
│   ├── ChatInterface.tsx       # Main chat interface
│   ├── MessageBubble.tsx       # Individual message display
│   └── ToolCallPanel.tsx       # Tool calls inspector panel
├── types/
│   └── index.ts            # TypeScript type definitions
├── App.tsx                 # Main app with state management
├── main.tsx                # Entry point
└── index.css               # Tailwind CSS directives
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework

## Features

- ✅ Create and manage multiple conversations
- ✅ Real-time chat interface with loading states
- ✅ View conversation history
- ✅ Inspect tool calls (collapsible panel)
- ✅ Delete conversations with confirmation
- ✅ Auto-scroll to latest message
- ✅ Responsive message display with timestamps

## Development

### Start Dev Server

```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## API Integration

The frontend communicates with the backend at `http://localhost:8000/api/v1`.

**Endpoints Used:**
- `POST /conversations` - Create new conversation
- `GET /conversations` - List all conversations
- `GET /conversations/{id}/messages` - Get conversation messages
- `DELETE /conversations/{id}` - Delete conversation
- `POST /chat` - Send message to agent
- `GET /tool-calls/session/{id}` - Get tool calls

## Component Architecture

### Separation of Concerns

**App.tsx** - State management and API orchestration
- Manages global state (conversations, messages, tool calls)
- Handles all API calls
- Coordinates component interactions

**ConversationList** - Sidebar navigation
- Displays conversation list
- Create/delete conversation buttons
- Highlights active conversation

**ChatInterface** - Main chat area
- Message display with auto-scroll
- Input form with loading states
- Integrates ToolCallPanel

**MessageBubble** - Individual message
- User vs Assistant styling
- Timestamp display
- Content formatting

**ToolCallPanel** - Tool call inspector
- Collapsible panel
- Expandable individual tool calls
- Input/output/error display

### Type Safety

All API responses and component props are fully typed using TypeScript interfaces defined in `types/index.ts`.

## Styling Principles

- **TailwindCSS utility classes** for all styling
- **No custom CSS** (except Tailwind directives)
- **Consistent color scheme**:
  - Blue (`blue-600`) for primary actions
  - Gray shades for UI chrome
  - White/Gray-100 for message bubbles
- **Responsive design** ready (though optimized for desktop)

## State Management

Simple React hooks-based state management:
- `useState` for local component state
- `useEffect` for side effects (loading data)
- No external state management library needed

State flows:
1. App loads → fetch conversations list
2. User selects conversation → fetch messages and tool calls
3. User sends message → optimistic UI update → API call → fetch updated data
4. User creates conversation → API call → refresh list → select new conversation

## Error Handling

- API errors logged to console
- User-friendly error messages displayed in chat
- Graceful fallbacks (empty states, loading indicators)
- Tool calls endpoint failures don't block message display

## Future Enhancements

- WebSocket for real-time streaming
- Markdown rendering for assistant messages
- Copy to clipboard for JSON responses
- Search/filter conversations
- Export conversation history
- Dark mode support
