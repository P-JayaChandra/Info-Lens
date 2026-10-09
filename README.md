# InfoLens — Intelligent Conversational Document Intelligence System

## Frontend Application (Member 1 Implementation)

InfoLens is a modern, responsive, academic productivity application designed for document understanding, grounded conversational Q&A, and study assistance.

---

## 🛠️ Technology Stack

- **Framework**: React.js (v19) + Vite (v5)
- **Styling**: Tailwind CSS (v4) with modern research workspace aesthetic
- **Routing**: React Router DOM (v7)
- **HTTP Client**: Axios with centralized request/response interceptors
- **Icons**: Lucide React
- **Forms & Validation**: Form state management with custom validators (Email, Password, File format/size)
- **Testing**: Vitest + React Testing Library + JSDOM

---

## 🚀 Quick Start & Running Locally

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_FIXTURES=true
```
> **Note**: When `VITE_USE_FIXTURES=true`, the frontend runs with isolated development fixtures. When Member 2's FastAPI backend is live, set `VITE_USE_FIXTURES=false`.

### 3. Launch Development Server
```bash
npm run dev
```

### 4. Run Automated Frontend Tests
```bash
npx vitest run
```

### 5. Build Production Bundle
```bash
npm run build
```

---

## 📂 Project Architecture

```
src/
├── api/                   # Centralized API Integration Layer
│   ├── client.js          # Axios client, interceptors & fixture fallback
│   ├── authApi.js         # Authentication endpoints
│   ├── documentApi.js     # Document management & upload APIs
│   ├── chatApi.js         # AI Q&A & conversation endpoints
│   ├── summaryApi.js      # Document summarization service
│   ├── questionApi.js     # Study question generator service
│   ├── quizApi.js         # Quiz runner & answer evaluation
│   ├── flashcardApi.js   # Flashcard deck & mastery persistence
│   └── settingsApi.js     # User preferences service
├── components/
│   ├── common/            # Reusable UI components (Button, Input, Modal, ConfirmDialog, Badge, etc.)
│   ├── layout/            # Application Shell, Sidebar, TopNav
│   ├── documents/         # UploadZone, DocumentCard, Reader, Viewer
│   ├── chat/              # ChatMessage, CitationCard, ChatInput
│   └── study/             # QuizRunner, FlashcardDeck
├── context/
│   ├── AuthContext.jsx       # Authentication session management
│   ├── DocumentContext.jsx   # Document selection & upload state
│   └── ToastContext.jsx      # Global toast notifications
├── hooks/                 # Custom React hooks (useAuth, useDocuments, useToast, useDebounce)
├── pages/
│   ├── Landing/           # Public Landing Page
│   ├── Auth/              # Login & Registration Screens
│   ├── Dashboard/         # Workspace Dashboard
│   ├── Documents/         # Document Library & Reader View
│   ├── Chat/              # Conversational AI Chat Interface
│   ├── Summaries/         # Document Summarization Interface
│   ├── Questions/         # Question Generator Interface
│   ├── Quiz/              # Interactive Quiz & Practice Mode
│   ├── Flashcards/        # Interactive 3D Flashcards
│   ├── History/           # Conversation History
│   └── Settings/          # User Settings & Accessibility
├── routes/                # Route definitions & ProtectedRoute guard
├── utils/                 # Formatters, Validators, and DEV_FIXTURES
└── tests/                 # Vitest test suites
```

---

## 🔗 Member 2 & Member 3 API Contracts

The frontend interacts with the backend through standardized REST endpoints:

| Service | Endpoint | Method | Payload / Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `/api/auth/login` | POST | `{ email, password }` |
| **Auth** | `/api/auth/register` | POST | `{ fullName, email, password }` |
| **Auth** | `/api/auth/me` | GET | Returns current user profile |
| **Documents** | `/api/documents` | GET | List user documents |
| **Documents** | `/api/documents/upload` | POST | Multipart FormData (`file`) |
| **Documents** | `/api/documents/:id` | DELETE / PATCH | Delete or rename document |
| **Chat** | `/api/chat/conversations` | GET / POST | List or create conversations |
| **Chat** | `/api/chat/conversations/:id/messages` | POST | `{ message, document_id }` |
| **Summaries**| `/api/summaries/generate` | POST | `{ document_id, length_mode }` |
| **Questions**| `/api/questions/generate` | POST | `{ document_id, question_type, count, difficulty }` |
| **Quiz** | `/api/quizzes/generate` | POST | `{ document_id, count }` |
| **Quiz** | `/api/quizzes/:id/submit` | POST | `{ answers: { q1: "option" } }` |
| **Flashcards**| `/api/flashcards/:id` | GET | Returns flashcard deck |

---

## ✅ Completed Features

- 🟢 **Public Landing Page**: Modern hero section, problem overview, workflow steps, feature highlights.
- 🟢 **Authentication Flow**: Login, Register, Logout, Form validation, Password visibility toggle, session persistence.
- 🟢 **Dashboard**: Data-driven statistics, recent documents grid, quick study shortcuts, loading skeletons, empty states.
- 🟢 **Document Upload Zone**: Drag-and-drop file picker, PDF/DOCX/TXT extension & size validation (max 25 MB), progress indicator, status tags (`Uploading`, `Processing`, `Ready`).
- 🟢 **Document Library**: Grid/List view toggle, title search, file format filtering, sorting, document reader drawer.
- 🟢 **Document Reader**: Extracted text view, search within document, page navigation, citation passage highlighting.
- 🟢 **Conversational AI Q&A**: Active document context picker, message history, multiline input, grounded citation cards that link directly to document text.
- 🟢 **Summarization Engine**: Executive overview & detailed section breakdown toggle, copy text, export .TXT file.
- 🟢 **Question Generator**: Multiple-choice, True/False, and Short answer generator with toggleable answer keys & explanations.
- 🟢 **Interactive Quiz Runner**: Question navigation, MC/TF selection, submit confirmation modal, score evaluation page with explanations.
- 🟢 **Flashcard Deck**: 3D CSS flip animation, keyboard shortcuts (Space, Left/Right arrows), mastery progress tracking (`Known` vs `For Review`), shuffle deck.
- 🟢 **Chat History**: Conversation search, update timestamps, open chat, rename and delete modals.
- 🟢 **Settings**: User profile, font size controls, citation highlighting preferences.
- 🟢 **Automated Vitest Test Suite**: 100% test pass rate for validators, API client, and fixture fallbacks.
