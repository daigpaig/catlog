import React, { useState } from "react";
import ChatBubble from "./ChatBubble";
import { apiService } from "@/services/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const data = await apiService.post<{ response: string }>("/chat", {
        message: input,
        timestamp: new Date().toISOString(),
      });

      setMessages([
        ...newMessages,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full h-full bg-[#1f0724] overflow-hidden text-white pt-4 px-2">
      {/* Message Area */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4">
        {messages.map((msg, i) => (
          <ChatBubble key={i} {...msg} />
        ))}
      </div>

      {/* Input */}
      <div className="border-t border-[#444] p-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="w-full px-4 py-2 rounded-lg border border-[#444] bg-[#2a2a2a] text-sm text-white placeholder-gray-400 focus:outline-none"
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
      </div>
    </div>
  );
};

export default ChatWindow;
