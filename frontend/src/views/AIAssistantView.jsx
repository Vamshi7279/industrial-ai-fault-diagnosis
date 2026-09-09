import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  User, 
  HelpCircle, 
  Terminal 
} from 'lucide-react';

export default function AIAssistantView({ selectedMachine }) {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: '🤖 **AI Industrial Maintenance Assistant initialized.** How can I assist you with machine sound telemetry, fault diagnosis, spare parts stock, or technician scheduling today?' }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "What machines currently have problems?",
    "Why did this machine generate an alert?",
    "When was this machine last serviced?",
    "When should this machine be serviced?",
    "What component may need replacement?",
    "Is the required spare part available?",
    "Who should handle this repair?",
    "Which manufacturer or service center should be contacted?"
  ];

  const handleSend = async (queryText) => {
    const textToSend = queryText || inputText;
    if (!textToSend.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: textToSend }]);
    if (!queryText) setInputText('');
    setLoading(true);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: textToSend,
          machine_type: selectedMachine
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { sender: 'bot', text: data.reply }]);
      }
    } catch (e) {
      console.error("AI Chat error:", e);
      setMessages(prev => [...prev, { sender: 'bot', text: "Error connecting to Agentic AI backend service." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bot className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl md:text-2xl font-extrabold text-white">Agentic AI Industrial Maintenance Assistant</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">Conversational AI reasoning interface over plant database, acoustic metrics, and maintenance schedules.</p>
        </div>
      </div>

      {/* Grid: Chat Interface & Quick Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface Column */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl flex flex-col h-[520px]">
          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex gap-3 text-xs ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'bot' && (
                  <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center flex-shrink-0 font-bold">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`p-3.5 rounded-2xl max-w-lg leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/30 font-semibold rounded-tr-none'
                    : 'bg-slate-900/80 text-slate-200 border border-slate-800 rounded-tl-none font-sans'
                }`}>
                  <div className="whitespace-pre-wrap">{m.text}</div>
                </div>

                {m.sender === 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center flex-shrink-0 font-bold">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="text-xs text-slate-400 font-mono animate-pulse flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" /> Multi-Agent AI system analyzing plant database & acoustic scores...
              </div>
            )}
          </div>

          {/* Chat Input Box */}
          <div className="pt-4 border-t border-slate-800 flex items-center gap-2">
            <input
              type="text"
              placeholder="Ask questions about faults, components, inventory, service dates..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1 bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 font-sans"
            />
            <button
              onClick={() => handleSend()}
              className="px-4 py-2.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-xs transition shadow-lg shadow-indigo-500/20 flex items-center gap-2"
            >
              <Send className="w-4 h-4" /> Send
            </button>
          </div>
        </div>

        {/* Quick Suggestion Chips Column */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-cyan-400" /> Suggested Manager Queries
          </h3>

          <div className="space-y-2">
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="w-full text-left p-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800/80 text-xs font-medium text-slate-300 hover:text-cyan-400 hover:border-cyan-500/30 transition duration-200"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
