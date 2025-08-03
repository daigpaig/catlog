import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const hours = Array.from({ length: 11 }, (_, i) => 8 + i);
const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const events = [
  {
    id: 1,
    title: "ECON 201",
    day: "Mon",
    start: "10:00",
    end: "11:20",
    color: "#3b82f6",
  },
  {
    id: 2,
    title: "CS 214",
    day: "Wed",
    start: "13:00",
    end: "14:20",
    color: "#f59e0b",
  },
];
const dayIndexMap: Record<string, number> = {
  Mon: 0,
  Tue: 1,
  Wed: 2,
  Thu: 3,
  Fri: 4,
};
const sample_schedules = [
  {
    id: 12,
    netid: "wpe1403",
    name: "Spring 2025 Schedule 1",
    term: "Spring 2025",
    created: "2025/04/20 05:31:31",
  },
  {
    id: 143,
    netid: "wpe1403",
    name: "Fall 2025 Schedule 1",
    term: "Fall 2025",
    created: "2025/08/14 14:00:03",
  },
];

const WeeklyCalendar = () => {
  const getTop = (time: string) => {
    const [hour, minute] = time.split(":").map(Number);
    return ((hour - 8 + minute / 60) / 11) * 100;
  };
  const getHeight = (start: string, end: string) => {
    const [sh, sm] = start.split(":").map(Number);
    const [eh, em] = end.split(":").map(Number);
    return ((eh + em / 60 - (sh + sm / 60)) / 11) * 100;
  };
  return (
    <div className="bg-[#1f0724] h-full w-full p-6 flex flex-col">
      <Select>
        <SelectTrigger className="bg-gray-800 text-white text-lg border-white w-md">
          <SelectValue placeholder="Schedule" />
        </SelectTrigger>
        <SelectContent className="bg-gray-900 text-white text-lg border border-gray-700">
          {sample_schedules.map((schedule) => (
            <SelectItem value={schedule.name} className="hover:bg-gray-700">
              {schedule.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <div
        className="grid h-full"
        style={{
          gridTemplateColumns: "3rem 1fr",
          gridTemplateRows: "2.5rem 1fr",
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
        <div className="grid grid-cols-5 grid-rows-11 bg-[#301934] w-full h-full relative">
          {hours.map((hour) =>
            days.map((day) => (
              <div
                key={`${day}-${hour}`}
                className="border-t border-dashed border-gray-700"
              ></div>
            ))
          )}
          {/* Overlaying courses */}
          {events.map((event) => {
            const left = `${dayIndexMap[event.day] * 20}%`;
            const width = "20%";
            const top = `${getTop(event.start)}%`;
            const height = `${getHeight(event.start, event.end)}%`;
            return (
              <div
                key={event.id}
                className="absolute text-white text-xs rounded-md px-2 py-1 opacity-70 shadow-md overflow-hidden shadow-none transition-shadow duration-300 cursor-pointer hover:shadow-sm hover:shadow-gray-400 hover:opacity-100"
                style={{
                  top,
                  left,
                  width,
                  height,
                  backgroundColor: event.color,
                }}
              >
                <div className="font-semibold text-sm">{event.title}</div>
                <div className="text-xs opacity-80">
                  {event.start}–{event.end}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default WeeklyCalendar;
