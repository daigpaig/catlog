import CourseRecommendation from "./CourseRecommendation";
import type { CourseRecommendationData } from "./CourseRecommendation";
import MultiCourseRecommendation from "./MultiCourseRecommendation";
import type { MultiCourseRecommendationData } from "./MultiCourseRecommendation";
import { useSchedule } from "@/contexts/ScheduleContext";
import { apiService } from "@/services/api";
import type { Course, Section } from "./SelectableCourseCard";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  structuredData?: {
    type?: string;
    [key: string]: any;
  };
}

const ChatBubble = ({ role, content, structuredData }: ChatBubbleProps) => {
  const { selectedScheduleId, setSelectedScheduleId, schedules, refreshSchedules } = useSchedule();

  const handleAddSection = async (sectionId: string, course: Course, section: Section) => {
    console.log("ChatBubble: handleAddSection called:", { sectionId, course, section, selectedScheduleId });
    
    if (!selectedScheduleId) {
      console.warn("ChatBubble: No selectedScheduleId available. Current schedules:", schedules);
      // Try to select the first available schedule automatically
      if (schedules && schedules.length > 0) {
        console.log("ChatBubble: Auto-selecting first available schedule:", schedules[0].id);
        setSelectedScheduleId(schedules[0].id);
        // Wait a moment for state to update, then try again
        setTimeout(async () => {
          await handleAddSection(sectionId, course, section);
        }, 100);
        return;
      }
      console.error("ChatBubble: No schedules available. Cannot add section.");
      return;
    }

    try {
      // Extract meeting days and times from section
      // Ensure meeting_days is an array of full day names (Mon, Tue, etc.)
      let meetingDays = section.meeting_days || [];
      // If meeting_days contains day codes (M, T, W, R, F), convert them
      const dayCodeMap: Record<string, string> = {
        'M': 'Mon', 'T': 'Tue', 'W': 'Wed', 'R': 'Thu', 'F': 'Fri',
        'S': 'Sat', 'U': 'Sun',
        'Mon': 'Mon', 'Tue': 'Tue', 'Wed': 'Wed', 'Thu': 'Thu', 'Fri': 'Fri',
        'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 'Thursday': 'Thu', 'Friday': 'Fri'
      };
      meetingDays = meetingDays.map((day: string) => dayCodeMap[day] || day).filter(Boolean);
      
      const startEnd = section.start_end || [];
      
      // Build course title
      const courseTitle = course.title || `${course.subject} ${course.catalog_number}`;
      
      const payload = {
        section_id: sectionId,
        course_subject: course.subject,
        course_number: course.catalog_number,
        course_title: courseTitle,
        section_number: section.section_number,
        meeting_days: meetingDays.length > 0 ? meetingDays : undefined,
        start_end: startEnd.length > 0 ? startEnd : undefined,
        instructors: (section.instructors && section.instructors.length > 0) ? section.instructors : undefined,
      };
      
      console.log("ChatBubble: Sending payload to backend:", payload);
      
      const result = await apiService.addScheduleCourse(selectedScheduleId, payload);
      
      console.log("ChatBubble: Add section response from backend:", result);
      console.log(`ChatBubble: Successfully added section ${sectionId} (${course.subject} ${course.catalog_number}) to schedule ${selectedScheduleId}`);
      
      // Dispatch custom event to trigger schedule courses refresh
      console.log(`ChatBubble: Dispatching scheduleCourseAdded event for schedule ${selectedScheduleId}`);
      window.dispatchEvent(new CustomEvent('scheduleCourseAdded', { detail: { scheduleId: selectedScheduleId } }));
    } catch (error: any) {
      console.error("ChatBubble: Failed to add section to schedule:", error);
      console.error("ChatBubble: Error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
    }
  };

  // Handle new alternating course recommendation format
  if (
    role === "assistant" &&
    structuredData?.type === "COURSE_RECOMMENDATION"
  ) {
    const recommendation: CourseRecommendationData = {
      intro:
        structuredData?.intro ||
        content ||
        "Here are some course recommendations:",
      items: Array.isArray(structuredData?.items) ? structuredData.items : [],
    };

    return (
      <div className="flex items-start gap-2.5 justify-start">
        <div className="flex flex-col max-w-full w-full">
          <CourseRecommendation
            recommendation={recommendation}
            onAddSection={handleAddSection}
            onDismiss={() => {
              console.log("Dismiss recommendation");
            }}
          />
        </div>
      </div>
    );
  }

  // Handle legacy multi-course recommendation format (for backward compatibility)
  if (
    role === "assistant" &&
    structuredData?.type === "MULTI_COURSE_RECOMMENDATION"
  ) {
    const recommendation: MultiCourseRecommendationData = {
      id: structuredData?.id,
      title: structuredData?.title,
      rationale:
        structuredData?.rationale ||
        content ||
        "Here are some course recommendations:",
      courses: Array.isArray(structuredData?.courses)
        ? structuredData.courses
        : [],
      priority: structuredData?.priority || "medium",
    };

    return (
      <div className="flex items-start gap-2.5 justify-start">
        <div className="flex flex-col max-w-full w-full">
          {content && content.trim() && (
            <div className="bg-gray-700 text-white rounded-e-xl rounded-es-xl opacity-70 p-4 mb-3">
              <p className="text-sm font-normal py-2.5 whitespace-pre-wrap">
                {content}
              </p>
            </div>
          )}
          <MultiCourseRecommendation
            recommendation={recommendation}
            onAddSection={handleAddSection}
            onDismiss={() => {
              console.log("Dismiss recommendation");
            }}
          />
        </div>
      </div>
    );
  }

  // Regular message bubble
  return (
    <div
      className={`flex items-start gap-2.5 ${
        role === "user" ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`flex flex-col max-w-[320px] leading-1.5 p-4 ${
          role === "user"
            ? "bg-[#3b82f6] text-white rounded-s-xl rounded-ee-xl opacity-70"
            : "bg-gray-700 text-white rounded-e-xl rounded-es-xl opacity-70"
        }`}
      >
        <p className="text-sm font-normal py-2.5 whitespace-pre-wrap">
          {content}
        </p>
      </div>
    </div>
  );
};

export default ChatBubble;
