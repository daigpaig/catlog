import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useCourseHover } from "@/contexts/CourseHoverContext";
import { ChevronDown, ChevronRight } from "lucide-react";

export type Section = {
  section_id?: string;
  section_number?: string;
  component?: string;
  instructors?: string[];
  meeting_days?: string[];
  start_end?: string[][];
  topic?: string;
  descriptions?: any[];
  distribution_areas?: string;
  foundational_disciplines?: string;
};

export type Course = {
  id: string;
  subject: string;
  catalog_number: string;
  title: string;
  units?: string | number;
  description?: string;
  meeting_days?: string[];
  start_end?: string[][];
  instructors?: string[];
  tags?: string[];
  school?: string;
  sections?: Section[];
};

interface SelectableCourseCardProps {
  course: Course;
  onAddSection: (sectionId: string, course: Course, section: Section) => void;
}

const SelectableCourseCard = ({ course, onAddSection }: SelectableCourseCardProps) => {
  const { setHoveredCourse, setHoveredSection } = useCourseHover();
  const sections = course.sections || [];
  const [isExpanded, setIsExpanded] = useState(sections.length > 0); // Auto-expand if sections exist

  return (
    <div
      onMouseEnter={() => setHoveredCourse(course)}
      onMouseLeave={() => {
        setHoveredCourse(null);
        setHoveredSection(null);
      }}
      className={cn(
        "flex flex-col gap-3 p-3 rounded-lg border bg-gray-800/50 border-gray-700 hover:bg-gray-800/70 transition-all"
      )}
    >
      <div className="flex items-start gap-3">
        {/* Course info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline gap-2 flex-wrap">
                <span className="font-semibold text-white text-sm">
                  {course.subject} {course.catalog_number}
                </span>
                {course.units && (
                  <span className="text-xs text-gray-400">
                    {course.units} unit{course.units !== 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-300 mt-1">{course.title}</p>
            </div>
          </div>

          {/* Meeting info */}
          {(course.meeting_days?.length || course.start_end?.length) && (
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-400">
              {course.meeting_days && course.meeting_days.length > 0 && (
                <span>{course.meeting_days.join(", ")}</span>
              )}
              {course.start_end &&
                course.start_end.length > 0 &&
                course.start_end.map(([start, end], i) => (
                  <span key={i}>
                    {start}-{end}
                  </span>
                ))}
            </div>
          )}

          {/* Instructors */}
          {course.instructors && course.instructors.length > 0 && (
            <div className="mt-1 text-xs text-gray-400">
              {course.instructors.join(", ")}
            </div>
          )}

          {/* Tags */}
          {course.tags && course.tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {course.tags.map((tag, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-xs rounded bg-gray-700/50 text-gray-300"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Sections expandable menu */}
      {sections.length > 0 && (
        <div className="mt-2 border-t border-gray-700 pt-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-300 transition-colors w-full mb-2"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <span>
              {sections.length} section{sections.length !== 1 ? "s" : ""}
            </span>
          </button>

          {isExpanded && (
            <div className="mt-2 space-y-2">
              {sections.map((section, index) => (
                <SectionBlock
                  key={section.section_id || index}
                  section={section}
                  course={course}
                  index={index}
                  onAdd={onAddSection}
                />
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* Show message if no sections */}
      {sections.length === 0 && (
        <div className="mt-2 text-xs text-gray-500 italic">
          No sections available for this course
        </div>
      )}
    </div>
  );
};

interface SectionBlockProps {
  section: Section;
  course: Course;
  index: number;
  onAdd: (sectionId: string, course: Course, section: Section) => void;
}

const SectionBlock = ({ section, course, index, onAdd }: SectionBlockProps) => {
  const { setHoveredSection, setHoveredCourse } = useCourseHover();

  // Color code sections - cycle through different colors
  const colors = [
    "bg-purple-500/20 border-purple-400/50 hover:bg-purple-500/30",
    "bg-green-500/20 border-green-400/50 hover:bg-green-500/30",
    "bg-yellow-500/20 border-yellow-400/50 hover:bg-yellow-500/30",
    "bg-pink-500/20 border-pink-400/50 hover:bg-pink-500/30",
    "bg-cyan-500/20 border-cyan-400/50 hover:bg-cyan-500/30",
  ];
  const colorClass = colors[index % colors.length];

  const sectionLabel = section.section_number
    ? `Section ${section.section_number}`
    : section.component
    ? `${section.component} Section`
    : `Section ${index + 1}`;

  // Generate section ID: use section_id if available, otherwise construct from course and section
  const sectionId = section.section_id || `${course.id}-${section.section_number || index}`;

  return (
    <div
      onMouseEnter={(e) => {
        e.stopPropagation(); // Prevent parent course hover
        setHoveredCourse(null); // Clear course hover
        setHoveredSection({ section, course, index });
      }}
      onMouseLeave={() => setHoveredSection(null)}
      className={cn(
        "p-2 rounded border transition-all text-xs flex items-start justify-between gap-2",
        colorClass
      )}
    >
      <div className="flex-1 min-w-0">
      <div className="font-semibold text-white mb-1">{sectionLabel}</div>
      {section.component && (
        <div className="text-gray-300 mb-1">Component: {section.component}</div>
      )}
      {section.meeting_days && section.meeting_days.length > 0 && (
        <div className="text-gray-400 mb-1">
          Days: {section.meeting_days.join(", ")}
        </div>
      )}
      {section.start_end && section.start_end.length > 0 && (
        <div className="text-gray-400 mb-1">
          {section.start_end.map(([start, end], i) => (
            <span key={i} className="mr-2">
              {start}-{end}
            </span>
          ))}
        </div>
      )}
      {section.instructors && section.instructors.length > 0 && (
        <div className="text-gray-400">
          Instructor{section.instructors.length > 1 ? "s" : ""}:{" "}
          {section.instructors.join(", ")}
        </div>
      )}
      </div>
      
      {/* Add button for section */}
      <Button
        onClick={(e) => {
          e.stopPropagation();
          onAdd(sectionId, course, section);
        }}
        size="sm"
        className="bg-blue-600 hover:bg-blue-700 flex-shrink-0 text-xs px-2 py-1 h-auto"
      >
        Add
      </Button>
    </div>
  );
};

export default SelectableCourseCard;
