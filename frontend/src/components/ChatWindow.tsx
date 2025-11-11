import React, { useState } from "react";
import ChatBubble from "./ChatBubble";
import { API_BASE_URL } from "@/config/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    const newMessages = [...messages, { role: "user", content: input }];

    console.log("Sending message:", { role: "user", content: input });

    setMessages(newMessages);
    setInput("");

    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      body: JSON.stringify({
        message: input,
        user_id: "demo_user",
        timestamp: new Date().toISOString(),
        majors: [],
        minors: [],
        schedule_preferences: "",
        self_description: "",
        locked_classes: [],
      }),
      headers: { "Content-Type": "application/json" },
    });

    const data = await res.json();
    setMessages([
      ...newMessages,
      { role: "assistant", content: data.response },
    ]);
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
