import { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useCourseHover } from "@/contexts/CourseHoverContext";
import { useAuth } from "@/contexts/AuthContext";
import { useSchedule } from "@/contexts/ScheduleContext";
import { apiService } from "@/services/api";
import CreateScheduleModal from "@/components/CreateScheduleModal";
import type { Schedule, ScheduleCourse } from "@/types/api";
import { X } from "lucide-react";

const hours = Array.from({ length: 11 }, (_, i) => 8 + i);
const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const dayIndexMap: Record<string, number> = {
  Mon: 0,
  Tue: 1,
  Wed: 2,
  Thu: 3,
  Fri: 4,
};

// Map day codes to day names
const dayCodeToName: Record<string, string> = {
  M: "Mon",
  T: "Tue",
  W: "Wed",
  R: "Thu",
  F: "Fri",
  S: "Sat",
  U: "Sun",
};

// Event type for calendar display
interface CalendarEvent {
  id: number;
  title: string;
  day: string;
  start: string;
  end: string;
  color: string;
  scheduleCourseId: number; // ID of the schedule course in the database
}

// Helper function to convert hex color to RGB
const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

// Lightweight MD5 implementation to match backend color generation
// Based on public domain MD5 implementation
const md5 = (str: string): string => {
  function md5cycle(x: number[], k: number[]) {
    let a = x[0], b = x[1], c = x[2], d = x[3];
    
    a = ff(a, b, c, d, k[0], 7, -680876936);
    d = ff(d, a, b, c, k[1], 12, -389564586);
    c = ff(c, d, a, b, k[2], 17, 606105819);
    b = ff(b, c, d, a, k[3], 22, -1044525330);
    a = ff(a, b, c, d, k[4], 7, -176418897);
    d = ff(d, a, b, c, k[5], 12, 1200080426);
    c = ff(c, d, a, b, k[6], 17, -1473231341);
    b = ff(b, c, d, a, k[7], 22, -45705983);
    a = ff(a, b, c, d, k[8], 7, 1770035416);
    d = ff(d, a, b, c, k[9], 12, -1958414417);
    c = ff(c, d, a, b, k[10], 17, -42063);
    b = ff(b, c, d, a, k[11], 22, -1990404162);
    a = ff(a, b, c, d, k[12], 7, 1804603682);
    d = ff(d, a, b, c, k[13], 12, -40341101);
    c = ff(c, d, a, b, k[14], 17, -1502002290);
    b = ff(b, c, d, a, k[15], 22, 1236535329);
    
    a = gg(a, b, c, d, k[1], 5, -165796510);
    d = gg(d, a, b, c, k[6], 9, -1069501632);
    c = gg(c, d, a, b, k[11], 14, 643717713);
    b = gg(b, c, d, a, k[0], 20, -373897302);
    a = gg(a, b, c, d, k[5], 5, -701558691);
    d = gg(d, a, b, c, k[10], 9, 38016083);
    c = gg(c, d, a, b, k[15], 14, -660478335);
    b = gg(b, c, d, a, k[4], 20, -405537848);
    a = gg(a, b, c, d, k[9], 5, 568446438);
    d = gg(d, a, b, c, k[14], 9, -1019803690);
    c = gg(c, d, a, b, k[3], 14, -187363961);
    b = gg(b, c, d, a, k[8], 20, 1163531501);
    a = gg(a, b, c, d, k[13], 5, -1444681467);
    d = gg(d, a, b, c, k[2], 9, -51403784);
    c = gg(c, d, a, b, k[7], 14, 1735328473);
    b = gg(b, c, d, a, k[12], 20, -1926607734);
    
    a = hh(a, b, c, d, k[5], 4, -378558);
    d = hh(d, a, b, c, k[8], 11, -2022574463);
    c = hh(c, d, a, b, k[11], 16, 1839030562);
    b = hh(b, c, d, a, k[14], 23, -35309556);
    a = hh(a, b, c, d, k[1], 4, -1530992060);
    d = hh(d, a, b, c, k[4], 11, 1272893353);
    c = hh(c, d, a, b, k[7], 16, -155497632);
    b = hh(b, c, d, a, k[10], 23, -1094730640);
    a = hh(a, b, c, d, k[13], 4, 681279174);
    d = hh(d, a, b, c, k[0], 11, -358537222);
    c = hh(c, d, a, b, k[3], 16, -722521979);
    b = hh(b, c, d, a, k[6], 23, 76029189);
    a = hh(a, b, c, d, k[9], 4, -640364487);
    d = hh(d, a, b, c, k[12], 11, -421815835);
    c = hh(c, d, a, b, k[15], 16, 530742520);
    b = hh(b, c, d, a, k[2], 23, -995338651);
    
    a = ii(a, b, c, d, k[0], 6, -198630844);
    d = ii(d, a, b, c, k[7], 10, 1126891415);
    c = ii(c, d, a, b, k[14], 15, -1416354905);
    b = ii(b, c, d, a, k[5], 21, -57434055);
    a = ii(a, b, c, d, k[12], 6, 1700485571);
    d = ii(d, a, b, c, k[3], 10, -1894986606);
    c = ii(c, d, a, b, k[10], 15, -1051523);
    b = ii(b, c, d, a, k[1], 21, -2054922799);
    a = ii(a, b, c, d, k[8], 6, 1873313359);
    d = ii(d, a, b, c, k[15], 10, -30611744);
    c = ii(c, d, a, b, k[6], 15, -1560198380);
    b = ii(b, c, d, a, k[13], 21, 1309151649);
    a = ii(a, b, c, d, k[4], 6, -145523070);
    d = ii(d, a, b, c, k[11], 10, -1120210379);
    c = ii(c, d, a, b, k[2], 15, 718787259);
    b = ii(b, c, d, a, k[9], 21, -343485551);
    
    x[0] = add32(a, x[0]);
    x[1] = add32(b, x[1]);
    x[2] = add32(c, x[2]);
    x[3] = add32(d, x[3]);
  }
  
  function cmn(q: number, a: number, b: number, x: number, s: number, t: number) {
    a = add32(add32(a, q), add32(x, t));
    return add32((a << s) | (a >>> (32 - s)), b);
  }
  
  function ff(a: number, b: number, c: number, d: number, x: number, s: number, t: number) {
    return cmn((b & c) | ((~b) & d), a, b, x, s, t);
  }
  
  function gg(a: number, b: number, c: number, d: number, x: number, s: number, t: number) {
    return cmn((b & d) | (c & (~d)), a, b, x, s, t);
  }
  
  function hh(a: number, b: number, c: number, d: number, x: number, s: number, t: number) {
    return cmn(b ^ c ^ d, a, b, x, s, t);
  }
  
  function ii(a: number, b: number, c: number, d: number, x: number, s: number, t: number) {
    return cmn(c ^ (b | (~d)), a, b, x, s, t);
  }
  
  function add32(a: number, b: number) {
    return (a + b) & 0xFFFFFFFF;
  }
  
  function rhex(n: number) {
    const s = '0123456789abcdef';
    let str = '';
    for (let j = 0; j <= 3; j++) {
      str += s.charAt((n >> (j * 8 + 4)) & 0x0F) + s.charAt((n >> (j * 8)) & 0x0F);
    }
    return str;
  }
  
  const utf8Encode = (str: string): number[] => {
    const utf8: number[] = [];
    for (let i = 0; i < str.length; i++) {
      let charcode = str.charCodeAt(i);
      if (charcode < 0x80) utf8.push(charcode);
      else if (charcode < 0x800) {
        utf8.push(0xc0 | (charcode >> 6), 0x80 | (charcode & 0x3f));
      } else if (charcode < 0xd800 || charcode >= 0xe000) {
        utf8.push(0xe0 | (charcode >> 12), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
      } else {
        i++;
        charcode = 0x10000 + (((charcode & 0x3ff) << 10) | (str.charCodeAt(i) & 0x3ff));
        utf8.push(0xf0 | (charcode >> 18), 0x80 | ((charcode >> 12) & 0x3f), 0x80 | ((charcode >> 6) & 0x3f), 0x80 | (charcode & 0x3f));
      }
    }
    return utf8;
  };
  
  const data = utf8Encode(str);
  const n = data.length * 8;
  const x = [1732584193, -271733879, -1732584194, 271733878];
  let i = 0;
  
  for (i = 0; i < data.length - 3; i += 4) {
    const k = [
      data[i] | (data[i + 1] << 8) | (data[i + 2] << 16) | (data[i + 3] << 24),
      data[i + 4] | (data[i + 5] << 8) | (data[i + 6] << 16) | (data[i + 7] << 24),
      data[i + 8] | (data[i + 9] << 8) | (data[i + 10] << 16) | (data[i + 11] << 24),
      data[i + 12] | (data[i + 13] << 8) | (data[i + 14] << 16) | (data[i + 15] << 24),
      data[i + 16] | (data[i + 17] << 8) | (data[i + 18] << 16) | (data[i + 19] << 24),
      data[i + 20] | (data[i + 21] << 8) | (data[i + 22] << 16) | (data[i + 23] << 24),
      data[i + 24] | (data[i + 25] << 8) | (data[i + 26] << 16) | (data[i + 27] << 24),
      data[i + 28] | (data[i + 29] << 8) | (data[i + 30] << 16) | (data[i + 31] << 24),
      data[i + 32] | (data[i + 33] << 8) | (data[i + 34] << 16) | (data[i + 35] << 24),
      data[i + 36] | (data[i + 37] << 8) | (data[i + 38] << 16) | (data[i + 39] << 24),
      data[i + 40] | (data[i + 41] << 8) | (data[i + 42] << 16) | (data[i + 43] << 24),
      data[i + 44] | (data[i + 45] << 8) | (data[i + 46] << 16) | (data[i + 47] << 24),
      data[i + 48] | (data[i + 49] << 8) | (data[i + 50] << 16) | (data[i + 51] << 24),
      data[i + 52] | (data[i + 53] << 8) | (data[i + 54] << 16) | (data[i + 55] << 24),
      data[i + 56] | (data[i + 57] << 8) | (data[i + 58] << 16) | (data[i + 59] << 24),
      data[i + 60] | (data[i + 61] << 8) | (data[i + 62] << 16) | (data[i + 63] << 24),
    ];
    md5cycle(x, k);
  }
  
  const tail = [];
  for (let j = i; j < data.length; j++) {
    tail.push(data[j]);
  }
  tail.push(0x80);
  while ((tail.length % 64) !== 56) {
    tail.push(0);
  }
  
  const lengthBytes = [];
  let m = n;
  for (let i = 0; i < 8; i++) {
    lengthBytes.push(m & 0xff);
    m >>>= 8;
  }
  tail.push(...lengthBytes);
  
  for (let i = 0; i < tail.length; i += 4) {
    const k = [
      tail[i] | (tail[i + 1] << 8) | (tail[i + 2] << 16) | (tail[i + 3] << 24),
    ];
    while (k.length < 16) k.push(0);
    md5cycle(x, k);
  }
  
  return rhex(x[0]) + rhex(x[1]) + rhex(x[2]) + rhex(x[3]);
};

// Generate course color based on subject (matches backend paper.nu-style color generation)
// Uses same MD5 algorithm as backend for exact color matching
const generateCourseColor = (subject: string): string => {
  if (!subject) {
    return "#3b82f6"; // Default blue
  }

  // Same color palette as backend - paper.nu inspired (MUST MATCH EXACTLY)
  const colors = [
    "#3b82f6", // Blue
    "#8b5cf6", // Purple
    "#ec4899", // Pink
    "#ef4444", // Red
    "#f59e0b", // Amber
    "#10b981", // Emerald
    "#06b6d4", // Cyan
    "#6366f1", // Indigo
    "#f97316", // Orange
    "#14b8a6", // Teal
    "#a855f7", // Violet
    "#e11d48", // Rose
    "#0ea5e9", // Sky
    "#84cc16", // Lime
    "#f43f5e", // Fuchsia
  ];

  // Normalize subject (uppercase, strip whitespace) - same as backend
  const normalizedSubject = subject.toUpperCase().trim();
  
  // Compute MD5 hash (same as backend)
  const hashHex = md5(normalizedSubject);
  
  // Convert hex string to integer (same as backend: int(hash_obj.hexdigest(), 16))
  // Use BigInt to handle large numbers correctly
  const hashInt = BigInt('0x' + hashHex);
  
  // Get color index using modulo (same as backend)
  const colorIndex = Number(hashInt % BigInt(colors.length));
  
  return colors[colorIndex];
};

const WeeklyCalendar = () => {
  const { hoveredCourse, hoveredSection } = useCourseHover();
  const { user } = useAuth();
  const {
    schedules,
    selectedScheduleId,
    setSelectedScheduleId,
    refreshSchedules,
    loading,
  } = useSchedule();
  const [scheduleCourses, setScheduleCourses] = useState<ScheduleCourse[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleCreateScheduleClick = () => {
    if (!user) {
      // Could show a toast/notification here instead of alert
      console.error("User must be logged in to create a schedule");
      return;
    }
    setIsCreateModalOpen(true);
  };

  const handleCreateScheduleSuccess = async (newSchedule: Schedule) => {
    // Refresh schedules list using context
    await refreshSchedules();

    // Select the newly created schedule
    if (newSchedule.id) {
      setSelectedScheduleId(newSchedule.id);
    }
  };

  const handleDeleteCourse = async (scheduleCourseId: number | undefined) => {
    if (!selectedScheduleId) {
      console.error("No schedule selected");
      return;
    }

    if (!scheduleCourseId || scheduleCourseId === undefined) {
      console.error("Invalid course ID for deletion:", scheduleCourseId);
      return;
    }

    // Optimistically remove the course from the UI immediately
    // This prevents the weird animation on other courses
    setEvents((prevEvents) => 
      prevEvents.filter(event => event.scheduleCourseId !== scheduleCourseId)
    );
    setScheduleCourses((prevCourses) => 
      prevCourses.filter(course => course.id !== scheduleCourseId)
    );

    try {
      await apiService.removeScheduleCourse(selectedScheduleId, scheduleCourseId);
      // Optionally refresh to ensure consistency, but UI already updated
      // const courses = await apiService.getScheduleCourses(selectedScheduleId);
      // setScheduleCourses(courses);
      // const calendarEvents = convertToCalendarEvents(courses);
      // setEvents(calendarEvents);
    } catch (error) {
      console.error("Failed to delete course:", error);
      // On error, refresh to restore the correct state
      const courses = await apiService.getScheduleCourses(selectedScheduleId);
      setScheduleCourses(courses);
      const calendarEvents = convertToCalendarEvents(courses);
      setEvents(calendarEvents);
    }
  };

  // Convert schedule courses to calendar events (using paper.nu-style colors)
  const convertToCalendarEvents = (
    courses: ScheduleCourse[]
  ): CalendarEvent[] => {
    const events: CalendarEvent[] = [];

    // Map day codes to full day names for conversion
    const dayCodeToFullName: Record<string, string> = {
      M: "Mon",
      T: "Tue",
      W: "Wed",
      R: "Thu",
      F: "Fri",
      S: "Sat",
      U: "Sun",
      Mon: "Mon",
      Tue: "Tue",
      Wed: "Wed",
      Thu: "Thu",
      Fri: "Fri",
      Monday: "Mon",
      Tuesday: "Tue",
      Wednesday: "Wed",
      Thursday: "Thu",
      Friday: "Fri",
    };

    courses.forEach((course) => {
      // Ensure course has an ID - log warning if missing
      if (!course.id) {
        console.warn("Course missing ID:", course);
        return; // Skip courses without IDs
      }

      const courseTitle =
        course.course_title ||
        `${course.course_subject || ""} ${course.course_number || ""}`.trim() ||
        "Untitled Course";
      // Use the stored color from the database (paper.nu style), or default to blue
      const hexColor = course.color || "#3b82f6";

      // Use meeting_days and start_end from the stored data
      // Typically: one time slot applies to all meeting days
      // e.g., meeting_days = ["Mon", "Wed", "Fri"], start_end = [["10:00", "11:20"]]
      if (
        course.meeting_days &&
        course.meeting_days.length > 0 &&
        course.start_end &&
        course.start_end.length > 0
      ) {
        // Use the first time slot for all meeting days (most common case)
        const timeSlot = course.start_end[0];
        if (timeSlot && Array.isArray(timeSlot) && timeSlot.length >= 2) {
          const [start, end] = timeSlot;
          if (start && end) {
            course.meeting_days.forEach((day) => {
              // Convert day code to full name if needed
              const fullDayName = dayCodeToFullName[day] || day;
              if (dayIndexMap[fullDayName] !== undefined && course.id) {
                // Create stable numeric ID based on course.id, day index, and time
                // This ensures React can properly track which elements changed
                const dayIndex = dayIndexMap[fullDayName];
                const timeHash = `${start}${end}`.replace(/:/g, '').replace(/-/g, '');
                // Combine course ID, day index (0-4), and first 4 digits of time hash for unique stable ID
                const stableId = course.id * 10000 + dayIndex * 1000 + (parseInt(timeHash.substring(0, 4)) || 0);
                
                events.push({
                  id: stableId,
                  title: courseTitle,
                  day: fullDayName,
                  start: start,
                  end: end,
                  color: hexColor, // Use the stored hex color from database
                  scheduleCourseId: course.id, // Store the schedule course ID for deletion
                });
              }
            });
          }
        }
      }
    });

    return events;
  };

  // Fetch courses when schedule is selected or when a course is added
  useEffect(() => {
    const fetchScheduleCourses = async () => {
      if (!selectedScheduleId) {
        setScheduleCourses([]);
        setEvents([]);
        return;
      }
      try {
        const courses = await apiService.getScheduleCourses(selectedScheduleId);
        setScheduleCourses(courses);
        // Convert schedule courses to calendar events
        const calendarEvents = convertToCalendarEvents(courses);
        setEvents(calendarEvents);
      } catch (error) {
        console.error("Failed to fetch schedule courses:", error);
        setScheduleCourses([]);
        setEvents([]);
      }
    };

    fetchScheduleCourses();

    // Listen for custom event when a course is added
    const handleScheduleCourseAdded = (event: Event) => {
      const customEvent = event as CustomEvent<{ scheduleId: number }>;
      const eventScheduleId = customEvent.detail?.scheduleId;

      // Refresh if the event is for the currently selected schedule
      // If no schedule is selected but we got an event, select that schedule and refresh
      if (eventScheduleId) {
        if (eventScheduleId === selectedScheduleId) {
          fetchScheduleCourses();
        } else if (!selectedScheduleId) {
          // Auto-select the schedule from the event and refresh
          setSelectedScheduleId(eventScheduleId);
          // The useEffect will run again when selectedScheduleId changes, which will fetch
        }
      }
    };

    window.addEventListener("scheduleCourseAdded", handleScheduleCourseAdded);

    return () => {
      window.removeEventListener(
        "scheduleCourseAdded",
        handleScheduleCourseAdded
      );
    };
  }, [selectedScheduleId]);

  const getTop = (time: string) => {
    const [hour, minute] = time.split(":").map(Number);
    return ((hour - 8 + minute / 60) / 11) * 100;
  };
  const getHeight = (start: string, end: string) => {
    const [sh, sm] = start.split(":").map(Number);
    const [eh, em] = end.split(":").map(Number);
    return ((eh + em / 60 - (sh + sm / 60)) / 11) * 100;
  };

  // Generate hover overlays - prioritize section hover over course hover
  const hoverOverlays: Array<{
    day: string;
    start: string;
    end: string;
    isSection: boolean;
    sectionIndex?: number;
    courseCode?: string;
    courseTitle?: string;
    color?: string; // Color for the hover overlay
  }> = [];

  // If a section is hovered, show only that section
  if (hoveredSection) {
    const { section, course, index } = hoveredSection;
    // Generate color based on subject (same as actual course blocks)
    const courseColor = generateCourseColor(course.subject);
    const courseTitle = course.title || `${course.subject} ${course.catalog_number}`;
    
    if (section.meeting_days && section.start_end) {
      section.meeting_days.forEach((dayCode) => {
        const dayName = dayCodeToName[dayCode];
        if (dayName) {
          section.start_end!.forEach(([start, end]) => {
            if (start && end) {
              hoverOverlays.push({
                day: dayName,
                start,
                end,
                isSection: true,
                sectionIndex: index,
                courseCode: `${course.subject} ${course.catalog_number}`,
                courseTitle: courseTitle,
                color: courseColor,
              });
            }
          });
        }
      });
    }
  }
  // Otherwise, if course is hovered, show all sections
  else if (
    hoveredCourse &&
    hoveredCourse.meeting_days &&
    hoveredCourse.start_end
  ) {
    // Generate color based on subject (same as actual course blocks)
    const courseColor = generateCourseColor(hoveredCourse.subject);
    const courseTitle = hoveredCourse.title || `${hoveredCourse.subject} ${hoveredCourse.catalog_number}`;
    
    hoveredCourse.meeting_days.forEach((dayCode) => {
      const dayName = dayCodeToName[dayCode];
      if (dayName) {
        hoveredCourse.start_end!.forEach(([start, end]) => {
          if (start && end) {
            hoverOverlays.push({
              day: dayName,
              start,
              end,
              isSection: false,
              courseCode: `${hoveredCourse.subject} ${hoveredCourse.catalog_number}`,
              courseTitle: courseTitle,
              color: courseColor,
            });
          }
        });
      }
    });
  }
  const selectedSchedule = schedules.find((s) => s.id === selectedScheduleId);

  return (
    <div className="bg-[#1f0724] h-full w-full p-6 flex flex-col gap-4">
      <div className="flex gap-2 items-center">
        <Select
          value={selectedScheduleId?.toString() || ""}
          onValueChange={(value) => setSelectedScheduleId(parseInt(value))}
        >
          <SelectTrigger className="bg-gray-800 text-white text-lg border-white w-md">
            <SelectValue
              placeholder={loading ? "Loading..." : "Select Schedule"}
            />
          </SelectTrigger>
          <SelectContent className="bg-gray-900 text-white text-lg border border-gray-700">
            {schedules.map((schedule) => (
              <SelectItem
                key={schedule.id}
                value={schedule.id.toString()}
                className="hover:bg-gray-700"
              >
                {schedule.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          onClick={handleCreateScheduleClick}
          variant="outline"
          className="bg-gray-800 text-white border-white hover:bg-gray-700"
        >
          + New Schedule
        </Button>
      </div>

      <CreateScheduleModal
        open={isCreateModalOpen}
        onOpenChange={setIsCreateModalOpen}
        onSuccess={handleCreateScheduleSuccess}
        existingSchedules={schedules}
      />

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
            // Use the hex color from the event (paper.nu style)
            const hexColor = event.color || "#3b82f6";

            // Convert hex to RGB for opacity/transparency if needed
            const rgb = hexToRgb(hexColor);
            const bgColor = rgb
              ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.9)`
              : hexColor;
            const borderColor = hexColor;
            const lighterColor = rgb
              ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.95)`
              : hexColor;

            // Create stable key for React - using scheduleCourseId + day + time ensures stable keys
            // This allows React to properly track which element was removed without re-rendering others
            const eventKey = `${event.scheduleCourseId}-${event.day}-${event.start}-${event.end}`;

            return (
              <div
                key={eventKey}
                className="absolute border-l-4 rounded-r-md px-2 py-1.5 shadow-lg cursor-pointer overflow-hidden text-white group"
                style={{
                  top,
                  left,
                  width: `calc(${width} - 0.25rem)`,
                  height: `max(${height}%, 2.5rem)`,
                  marginLeft: "0.125rem",
                  backgroundColor: bgColor,
                  borderColor: borderColor,
                  // Only animate hover effects, not position (prevents weird movement on delete)
                  transition: 'background-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = lighterColor;
                  e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)';
                  e.currentTarget.style.transform = 'scale(1.02)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = bgColor;
                  e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <div className="flex items-start justify-between gap-1 h-full">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-xs leading-tight truncate mb-0.5">
                      {event.title}
                    </div>
                    <div className="text-[10px] opacity-90 font-medium">
                      {event.start}–{event.end}
                    </div>
                  </div>
                  {event.scheduleCourseId && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (event.scheduleCourseId) {
                          handleDeleteCourse(event.scheduleCourseId);
                        }
                      }}
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-150 flex-shrink-0 p-0.5 hover:bg-white/20 rounded"
                      title="Remove course from schedule"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
          {/* Hover overlays for course recommendations - preview of actual course block */}
          {hoverOverlays.map((overlay, index) => {
            const dayIndex = dayIndexMap[overlay.day];
            if (dayIndex === undefined) return null;

            const left = `${dayIndex * 20}%`;
            const width = "20%";
            const top = `${getTop(overlay.start)}%`;
            const height = `${getHeight(overlay.start, overlay.end)}%`;

            // Use the course's subject-based color (same as actual blocks)
            const hexColor = overlay.color || "#3b82f6";
            const rgb = hexToRgb(hexColor);
            
            // Low opacity background (15% opacity) - subtle preview
            const hoverBgColor = rgb
              ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.15)`
              : `${hexColor}26`; // Fallback with hex opacity (~15%)
            const hoverBorderColor = hexColor;
            // Text color matches the subject color but with good contrast
            const hoverTextColor = rgb
              ? `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.85)`
              : hexColor;

            return (
              <div
                key={`hover-${overlay.courseCode}-${overlay.day}-${overlay.start}-${overlay.end}-${index}`}
                className="absolute rounded-r-md px-2 py-1.5 pointer-events-none"
                style={{
                  top,
                  left,
                  width: `calc(${width} - 0.25rem)`,
                  height: `max(${height}%, 2.5rem)`,
                  marginLeft: "0.125rem",
                  backgroundColor: hoverBgColor,
                  borderColor: hoverBorderColor,
                  // Dotted/dashed border all around - preview style
                  border: "2px dashed",
                  borderLeft: "4px solid", // Keep left border solid and thicker like actual blocks
                  borderLeftColor: hoverBorderColor,
                  // No transition on position - prevents animation when courses are removed
                }}
              >
                <div className="flex items-start justify-between gap-1 h-full">
                  <div className="flex-1 min-w-0">
                    <div
                      className="font-semibold text-xs leading-tight truncate mb-0.5"
                      style={{ color: hoverTextColor }}
                    >
                      {overlay.courseTitle || overlay.courseCode}
                    </div>
                    <div
                      className="text-[10px] opacity-90 font-medium"
                      style={{ color: hoverTextColor }}
                    >
                      {overlay.start}–{overlay.end}
                    </div>
                  </div>
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
