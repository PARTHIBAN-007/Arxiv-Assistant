import React, { useState, useRef, useEffect } from "react";

function App() {
  const [messages, setMessages] = useState([
    { sender: "assistant", text: "Hello! How can I help you with Arxiv papers today?" }
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-100 flex flex-col items-center">
      <header className="w-full bg-white shadow-md py-6 mb-6">
        <h1 className="text-3xl font-extrabold text-center text-blue-700 tracking-tight">
          Arxiv Assistant
        </h1>
        
      </header>
      <main className="flex-1 w-full max-w-2xl flex flex-col bg-white rounded-2xl shadow-lg p-0 border border-gray-100">
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-4 custom-scrollbar" style={{ minHeight: 400 }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`px-5 py-3 rounded-2xl shadow-sm max-w-[75%] text-base ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <form
          onSubmit={handleSend}
          className="flex gap-3 border-t border-gray-200 px-6 py-4 bg-gray-50 rounded-b-2xl"
        >
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white text-gray-800 shadow-sm"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold shadow hover:bg-blue-700 transition"
          >
            Send
          </button>
        </form>
      </main>
      <footer className="mt-8 mb-4 text-gray-400 text-xs text-center">
        &copy; {new Date().getFullYear()} Arxiv Assistant. All rights reserved.
      </footer>
    </div>
  );
}

export default App;