import React, { useState, useEffect } from "react";
import { CircleQuestionMarkIcon, X } from "lucide-react";
import { Button } from "./ui/button";
import { apiService } from "@/services/api";

const hours = Array.from({ length: 11 }, (_, i) => 8 + i);
const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

interface SchedulingPreferencesProps {
  netid: string;
  unavailable_times: string[];
  prefer_avoid_times: string[];
  onUpdate?: () => void;
  fullProfile?: {
    netid: string;
    majors: string[];
    minors?: string[];
    classes_already_taken?: string[];
    vocational_interests?: string[];
    favorite_profs?: string[];
    disliked_profs?: string[];
    earliest_class_time?: string;
    locked_classes?: string[];
    self_description?: string;
    unavailable_times?: string[];
    prefer_avoid_times?: string[];
  };
}

type TimeSlotStatus = "none" | "unavailable" | "prefer_avoid";

const SchedulingPreferences: React.FC<SchedulingPreferencesProps> = ({
  netid,
  unavailable_times: initialUnavailable,
  prefer_avoid_times: initialPreferAvoid,
  onUpdate,
  fullProfile,
}) => {
  // Create a map of time slot statuses
  const getTimeSlotKey = (day: string, hour: number) => `${day}-${hour}`;

  const [timeSlots, setTimeSlots] = useState<Map<string, TimeSlotStatus>>(
    new Map()
  );
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Initialize time slots from props
  useEffect(() => {
    const slots = new Map<string, TimeSlotStatus>();
    
    // Initialize all slots as "none"
    days.forEach((day) => {
      hours.forEach((hour) => {
        slots.set(getTimeSlotKey(day, hour), "none");
      });
    });

    // Mark unavailable times
    initialUnavailable.forEach((key) => {
      slots.set(key, "unavailable");
    });

    // Mark prefer avoid times (unavailable takes precedence)
    initialPreferAvoid.forEach((key) => {
      if (slots.get(key) === "none") {
        slots.set(key, "prefer_avoid");
      }
    });

    setTimeSlots(slots);
    setHasChanges(false);
  }, [initialUnavailable, initialPreferAvoid]);

  const handleTimeSlotClick = (day: string, hour: number, status: "unavailable" | "prefer_avoid") => {
    const key = getTimeSlotKey(day, hour);
    const currentStatus = timeSlots.get(key) || "none";

    setTimeSlots((prev) => {
      const newSlots = new Map(prev);
      
      // Toggle logic:
      // - If clicking unavailable: toggle between unavailable and none
      // - If clicking prefer_avoid: cycle through none -> prefer_avoid -> unavailable -> none
      if (status === "unavailable") {
        if (currentStatus === "unavailable") {
          newSlots.set(key, "none");
        } else {
          newSlots.set(key, "unavailable");
        }
      } else if (status === "prefer_avoid") {
        if (currentStatus === "none") {
          newSlots.set(key, "prefer_avoid");
        } else if (currentStatus === "prefer_avoid") {
          newSlots.set(key, "unavailable");
        } else {
          // currentStatus === "unavailable"
          newSlots.set(key, "none");
        }
      }
      
      return newSlots;
    });
    
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Convert time slots map to arrays
      const unavailable: string[] = [];
      const preferAvoid: string[] = [];

      timeSlots.forEach((status, key) => {
        if (status === "unavailable") {
          unavailable.push(key);
        } else if (status === "prefer_avoid") {
          preferAvoid.push(key);
        }
      });

      // Use fullProfile as base to ensure we send all required fields
      const baseProfile = fullProfile || {
        netid,
        majors: [],
        minors: [],
        classes_already_taken: [],
        vocational_interests: [],
        favorite_profs: [],
        disliked_profs: [],
        earliest_class_time: undefined,
        locked_classes: [],
        self_description: "",
        unavailable_times: [],
        prefer_avoid_times: [],
      };

      await apiService.updateProfile({
        netid: baseProfile.netid,
        majors: baseProfile.majors || [],
        minors: baseProfile.minors || [],
        classes_already_taken: baseProfile.classes_already_taken || [],
        vocational_interests: baseProfile.vocational_interests || [],
        favorite_profs: baseProfile.favorite_profs || [],
        disliked_profs: baseProfile.disliked_profs || [],
        earliest_class_time: baseProfile.earliest_class_time,
        locked_classes: baseProfile.locked_classes || [],
        self_description: baseProfile.self_description || "",
        unavailable_times: unavailable,
        prefer_avoid_times: preferAvoid,
      });

      setHasChanges(false);
      
      // Refresh profile in parent component
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error("Failed to save scheduling preferences:", error);
      alert("Failed to save scheduling preferences. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const getTimeSlotStatus = (day: string, hour: number): TimeSlotStatus => {
    return timeSlots.get(getTimeSlotKey(day, hour)) || "none";
  };

  const getTimeSlotBgColor = (status: TimeSlotStatus): string => {
    switch (status) {
      case "unavailable":
        return "bg-red-900/30 border-red-500/50";
      case "prefer_avoid":
        return "bg-yellow-900/30 border-yellow-500/50";
      default:
        return "";
    }
  };

  return (
    <div className="overflow-auto h-full bg-[#301934] rounded-lg p-4 my-3 text-white">
      <h2 className="text-lg font-bold mb-2">Scheduling Preferences</h2>
      <p className="text-gray-300 text-sm mb-4">
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
        <div className="grid grid-cols-5 grid-rows-11 bg-[#301934] w-full h-full relative">
          {hours.map((hour) =>
            days.map((day) => {
              const status = getTimeSlotStatus(day, hour);
              const bgColor = getTimeSlotBgColor(status);
              
              return (
                <div
                  key={`${day}-${hour}`}
                  className={`border-t border-dashed border-gray-700 hover:bg-gray-600 flex justify-evenly items-center group hover:cursor-pointer transition-colors ${bgColor}`}
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTimeSlotClick(day, hour, "unavailable");
                    }}
                    className={`text-red-500 ${
                      status === "unavailable"
                        ? "opacity-100"
                        : "opacity-0 group-hover:opacity-100"
                    } hover:cursor-pointer w-8 h-8 rounded-full hover:bg-gray-500 flex items-center justify-center transition-opacity`}
                    title="Mark as unavailable"
                  >
                    <X />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTimeSlotClick(day, hour, "prefer_avoid");
                    }}
                    className={`text-yellow-400 ${
                      status === "prefer_avoid"
                        ? "opacity-100"
                        : "opacity-0 group-hover:opacity-100"
                    } hover:cursor-pointer w-8 h-8 rounded-full hover:bg-gray-500 flex items-center justify-center transition-opacity`}
                    title="Prefer to avoid"
                  >
                    <CircleQuestionMarkIcon />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
      <div className="flex items-center justify-between mt-4">
        <div className="text-sm text-gray-400">
          {hasChanges && "You have unsaved changes"}
        </div>
        <Button
          onClick={handleSave}
          disabled={saving || !hasChanges}
          className="bg-gray-800 hover:bg-gray-600 hover:cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? "Saving..." : "Save"}
        </Button>
      </div>
    </div>
  );
};

export default SchedulingPreferences;
