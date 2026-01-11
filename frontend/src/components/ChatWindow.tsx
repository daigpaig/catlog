import { useState } from "react";
import ChatBubble from "./ChatBubble";
import { apiService } from "@/services/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  structuredData?: {
    type?: string;
    [key: string]: any;
  };
};

const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const newMessages: Message[] = [
      ...messages,
      { role: "user", content: input },
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const data = await apiService.post<{
        response: string;
        structuredData?: {
          type?: string;
          [key: string]: any;
        };
      }>("/chat", {
        message: input,
        timestamp: new Date().toISOString(),
      });

      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: data.response,
          structuredData: data.structuredData,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      let errorMessage = "Sorry, something went wrong. Please try again.";
      if (error instanceof Error) {
        console.error("Error details:", error.message);
        errorMessage = `Error: ${error.message}`;
      }
      setMessages([
        ...newMessages,
        {
          role: "assistant",
          content: errorMessage,
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
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">Welcome! 👋</p>
            <p className="text-sm">
              Ask me about courses, and I'll help you find the perfect schedule.
            </p>
          </div>
        )}
        {messages.map((msg, i) => (
          <ChatBubble key={i} {...msg} />
        ))}
        {loading && (
          <div className="flex items-start gap-2.5 justify-start">
            <div className="bg-gray-700 text-white rounded-e-xl rounded-es-xl opacity-70 p-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-[#444] p-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="w-full px-4 py-2 rounded-lg border border-[#444] bg-[#2a2a2a] text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={loading}
        />
      </div>
    </div>
  );
};

export default ChatWindow;
