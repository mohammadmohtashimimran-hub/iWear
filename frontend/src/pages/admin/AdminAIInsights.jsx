import { useEffect, useRef, useState } from 'react'
import { aiQuery, aiIntents } from '../../api'

/**
 * AI Business Insights Assistant — chat-style interface to the keyword-based
 * intent matching backend. Sends natural-language queries to
 * POST /api/ai-assistant/query and renders the returned summary + table.
 */
export default function AdminAIInsights() {
  const [intents, setIntents] = useState([])
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: 'Hi! Ask me about your store. Try "sales today", "monthly profit", or "best selling products".',
    },
  ])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const bodyRef = useRef(null)

  useEffect(() => {
    aiIntents().then(setIntents).catch(() => setIntents([]))
  }, [])

  useEffect(() => {
    if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight
  }, [messages])

  const send = async (text) => {
    const q = (text ?? input).trim()
    if (!q || busy) return
    setMessages(m => [...m, { role: 'user', text: q }])
    setInput('')
    setBusy(true)
    try {
      const res = await aiQuery(q)
      setMessages(m => [...m, {
        role: 'bot',
        text: res.summary || 'No response',
        table: res.table,
        intent: res.intent,
      }])
    } catch (e) {
      setMessages(m => [...m, { role: 'bot', text: `Error: ${e.message}`, error: true }])
    } finally {
      setBusy(false)
    }
  }

  const onSubmit = (e) => { e.preventDefault(); send() }

  return (
    <div>
      <h2 className="section-title">AI Business Insights</h2>
      <p className="section-subtitle">Ask questions about your store in plain English. Powered by intent matching over predefined queries.</p>

      <div className="ai-page">
        <aside className="ai-suggestions">
          <h3>Try asking</h3>
          <div className="ai-suggestion-list">
            {(intents.length ? intents : [
              { name: 'Daily Sales', examples: ['sales today'] },
              { name: 'Monthly Profit', examples: ['monthly profit'] },
              { name: 'Best Selling Products', examples: ['best selling products'] },
              { name: 'Low Stock', examples: ['low stock'] },
            ]).map((it) => {
              const ex = (it.examples && it.examples[0]) || it.name.toLowerCase()
              return (
                <button key={it.id || it.name} type="button" onClick={() => send(ex)}>
                  {it.name}
                </button>
              )
            })}
          </div>
        </aside>

        <div className="ai-chat">
          <div className="ai-chat-body" ref={bodyRef}>
            {messages.map((m, i) => (
              <div key={i} className={`ai-msg ${m.role}`}>
                {m.intent && <div style={{ fontSize: '0.72rem', opacity: 0.7, marginBottom: 4 }}>Intent: {m.intent}</div>}
                <div>{m.text}</div>
                {m.table && m.table.length > 0 && (
                  <table className="ai-msg-table">
                    <thead>
                      <tr>{Object.keys(m.table[0]).map(k => <th key={k}>{k}</th>)}</tr>
                    </thead>
                    <tbody>
                      {m.table.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((v, j) => <td key={j}>{String(v ?? '')}</td>)}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ))}
            {busy && <div className="ai-msg bot"><em>Thinking…</em></div>}
          </div>
          <form className="ai-input-row" onSubmit={onSubmit}>
            <input
              type="text"
              placeholder="e.g. sales today, monthly profit, low stock…"
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={busy}
            />
            <button type="submit" className="btn btn-primary" disabled={busy || !input.trim()}>Send</button>
          </form>
        </div>
      </div>
    </div>
  )
}
