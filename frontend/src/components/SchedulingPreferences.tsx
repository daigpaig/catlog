import React from "react";
import { CircleQuestionMarkIcon, Pencil, X } from "lucide-react";
import { Button } from "./ui/button";

const hours = Array.from({ length: 11 }, (_, i) => 8 + i);
const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

const SchedulingPreferences = () => {
  return (
    <div className="overflow-auto h-full bg-[#301934] rounded-lg p-4 my-3 text-white">
      <h2 className="text-lg font-bold">Scheduling Preferences</h2>
      <p>
        Indicate your scheduling preferences here. Click the red cross if you
        are absolutely unavailable, and the yellow question mark if you would
        prefer to avoid the time.
      </p>
      <div
        className="grid h-full"
        style={{
          gridTemplateColumns: "3rem 1fr",
          gridTemplateRows: "2.5rem 30rem",
        }}
      >
        {/* Top-left (empty) */}
        <div className="w-full h-full"></div>

        {/* Top-right (day labels) */}
        <div className="grid grid-cols-5 items-end h-full">
          {days.map((day) => (
            <div
              key={day}
              className="text-center text-gray-300 text-sm font-thin pb-1"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Bottom-left (time labels) */}
        <div className="grid grid-rows-11 w-full h-full">
          {hours.map((hour) => (
            <div
              key={hour}
              className="text-gray-300 font-thin flex items-start justify-end pr-2 text-sm"
            >
              {hour}:00
            </div>
          ))}
        </div>

        {/* Bottom-right (grid) */}
        <div className="grid grid-cols-5 grid-rows-11 bg-[#301934] w-full h-full relative bg-gray-800">
          {hours.map((hour) =>
            days.map((day) => (
              <div
                key={`${day}-${hour}`}
                className="border-t border-dashed border-gray-700 hover:bg-gray-600 flex justify-evenly items-center group  hover:cursor-pointer"
              >
                <button className="text-red-500 opacity-0 group-hover:opacity-100 hover:cursor-pointer w-8 h-8 rounded-full hover:bg-gray-500 flex items-center justify-center">
                  <X />
                </button>
                <button className="text-yellow-400 opacity-0 group-hover:opacity-100 hover:cursor-pointer w-8 h-8 rounded-full hover:bg-gray-500 flex items-center justify-center">
                  <CircleQuestionMarkIcon />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
      <Button className="mt-4 bg-gray-800 hover:bg-gray-600 hover:cursor-pointer">
        Save
      </Button>
    </div>
  );
};

export default SchedulingPreferences;
