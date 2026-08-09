import { useEffect, useRef, useState } from 'react'

// Your Flask backend from server.py. Change this if you run it on a different port.
const API_URL = 'http://localhost:5000/api/chat'

// A few starter questions so the empty state isn't just a blank box.
// PLACEHOLDER — swap these once you know what's actually in your document
// (admissions, fees, hostel, placements, etc. are just examples).
const SUGGESTED_QUESTIONS = [
  'What is the admission process?',
  'What is the fee structure?',
  'Is hostel accommodation available?',
  'When do placements happen?',
]

let nextId = 1

function App() {
  // Every message on screen: { id, role: 'user' | 'bot' | 'error', text }
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const scrollRef = useRef(null)

  // Keep the chat scrolled to the newest message.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isLoading])

  async function sendQuestion(question) {
    const trimmed = question.trim()
    if (!trimmed || isLoading) return

    setMessages((prev) => [...prev, { id: nextId++, role: 'user', text: trimmed }])
    setInput('')
    setIsLoading(true)

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmed }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.error || 'Something went wrong.')
      }

      setMessages((prev) => [...prev, { id: nextId++, role: 'bot', text: data.answer }])
    } catch (err) {
      const isNetworkError = err instanceof TypeError
      const text = isNetworkError
        ? "Sahayak can't reach the server right now. Make sure server.py is running on port 5000."
        : err.message

      setMessages((prev) => [...prev, { id: nextId++, role: 'error', text }])
    } finally {
      setIsLoading(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    sendQuestion(input)
  }

  return (
    <div className="app-shell">
      <header className="header">
        <h1>C.U. Shah Sahayak</h1>
        <p>Ask about the university — answers straight from official documents</p>
      </header>

      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="empty-state">
            <span className="slice">🎓</span>
            <h2>What do you want to know?</h2>
            <p>Every answer here is pulled from official university documents.</p>
            <div className="chip-row">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button key={q} className="chip" onClick={() => sendQuestion(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message-row ${msg.role === 'user' ? 'user' : 'bot'}`}>
            <div className={`ticket ${msg.role}`}>
              <span className="eyebrow">
                {msg.role === 'user' ? 'You' : msg.role === 'error' ? 'Error' : 'Sahayak'}
              </span>
              <p className="body-text">{msg.text}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message-row bot">
            <div className="ticket bot">
              <span className="eyebrow">Sahayak</span>
              <div className="typing-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="input-dock">
        <div className="perforation" />
        <form className="input-row" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about admissions, fees, facilities..."
            disabled={isLoading}
            autoFocus
          />
          <button type="submit" className="send-btn" disabled={isLoading || !input.trim()} aria-label="Send question">
            ➤
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
