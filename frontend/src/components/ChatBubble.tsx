import React from "react";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
}

const ChatBubble = ({ role, content }: ChatBubbleProps) => {
  return (
    <div
      className={`flex items-start gap-2.5 ${
        role == "user" ? "justify-end" : ""
      }`}
    >
      <div
        className={`flex flex-col max-w-[320px] leading-1.5 p-4 ${
          role == "user"
            ? "bg-[#3b82f6] text-white rounded-s-xl rounded-ee-xl opacity-70"
            : "bg-gray-700 text-white rounded-e-xl rounded-es-xl opacity-70"
        }`}
      >
        <p className="text-sm font-normal py-2.5">{content}</p>
      </div>
    </div>
  );
};

export default ChatBubble;
