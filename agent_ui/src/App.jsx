import React, { useState } from "react";

function App() {
  const [messages, setMessages] = useState([
    { sender: "assistant", text: "Hello! How can I help you with Arxiv papers today?" }
  ]);
  const [input, setInput] = useState("");

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center">
      <header className="w-full bg-white shadow p-4 mb-4">
        <h1 className="text-2xl font-bold text-center text-gray-800">Arxiv Assistant</h1>
      </header>
      <main className="flex-1 w-full max-w-xl flex flex-col bg-white rounded-lg shadow p-4">
        <div className="flex-1 overflow-y-auto mb-4 space-y-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`px-4 py-2 rounded-lg max-w-xs ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <form onSubmit={handleSend} className="flex gap-2">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;