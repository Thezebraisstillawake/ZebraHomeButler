import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import './App.css'

interface Message {
  id: number
  content: string
  role: 'user' | 'ai'
  timestamp: number
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      content: '你好！我是 StudyMate，你的 AI 学习助手 📚 有什么可以帮你的吗？',
      role: 'ai',
      timestamp: Date.now(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return

    const userMsg: Message = {
      id: Date.now(),
      content: trimmed,
      role: 'user',
      timestamp: Date.now(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed }),
      })

      const data = await res.json()

      const aiMsg: Message = {
        id: Date.now() + 1,
        content: data.reply || '抱歉，我没有理解你的意思。',
        role: 'ai',
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: Date.now() + 1,
        content: '网络错误，请稍后重试 😢',
        role: 'ai',
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">📚</div>
          <h1 className="title">StudyMate</h1>
          <span className="subtitle">AI学习助手</span>
        </div>
      </header>

      <main className="message-list">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.role}`}>
            {msg.role === 'ai' && (
              <div className="avatar ai-avatar">🤖</div>
            )}
            <div className={`bubble ${msg.role}`}>
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div className="avatar user-avatar">👤</div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message-wrapper ai">
            <div className="avatar ai-avatar">🤖</div>
            <div className="bubble ai">
              <div className="typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <footer className="input-area">
        <div className="input-wrapper">
          <textarea
            className="text-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的问题..."
            rows={1}
            disabled={loading}
          />
          <button
            className={`send-btn ${input.trim() ? 'active' : ''}`}
            onClick={sendMessage}
            disabled={!input.trim() || loading}
          >
            {loading ? '...' : '发送'}
          </button>
        </div>
      </footer>
    </div>
  )
}

export default App