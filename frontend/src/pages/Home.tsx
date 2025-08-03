import React, { useRef, useState } from "react";
import WeeklyCalendar from "../components/WeeklyCalendar";
import ChatWindow from "../components/ChatWindow";
import HeaderBar from "../components/HeaderBar";

function Home() {
  const [leftWidth, setLeftWidth] = useState(400);
  const [isDragging, setIsDragging] = useState(false);

  const minLeftWidth = 400;
  const minRightWidth = 500;

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = leftWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = startWidth + (e.clientX - startX);
      const maxWidth = window.innerWidth - minRightWidth;
      setLeftWidth(Math.max(minLeftWidth, Math.min(newWidth, maxWidth)));
    };

    const handleMouseUp = () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  return (
    <div className="flex flex-col h-screen">
      <HeaderBar />
      <div
        className={`flex w-screen h-full overflow-hidden ${
          isDragging ? "select-none" : ""
        }`}
      >
        {/* Chat */}
        <div
          style={{ width: `${leftWidth}px` }}
          className="h-full overflow-auto"
        >
          <ChatWindow />
        </div>

        {/* Resizer */}
        <div
          onMouseDown={handleMouseDown}
          className="w-2 cursor-col-resize bg-gray-600 hover:bg-gray-400"
        />

        {/* Schedule */}
        <div className="flex-1 h-full overflow-auto">
          <WeeklyCalendar />
        </div>
      </div>
    </div>
  );
}

export default Home;
