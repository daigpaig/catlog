import { Button } from "@/components/ui/button";
import SelectableCourseCard from "./SelectableCourseCard";
import type { Course } from "./SelectableCourseCard";

export interface CourseRecommendationItem {
  type: "course" | "description";
  course?: Course;
  description?: string;
}

export interface CourseRecommendationData {
  intro: string;
  items: CourseRecommendationItem[];
}

interface CourseRecommendationProps {
  recommendation: CourseRecommendationData;
  onAddSection?: (sectionId: string, course: Course, section: import("./SelectableCourseCard").Section) => void;
  onDismiss?: () => void;
}

const CourseRecommendation = ({
  recommendation,
  onAddSection,
  onDismiss,
}: CourseRecommendationProps) => {

  return (
    <div className="rounded-2xl border border-gray-700 bg-gray-800/50 p-4 space-y-4">
      {/* Intro message */}
      <p className="text-sm text-gray-300 leading-relaxed">
        {recommendation.intro}
      </p>

      {/* Alternating course blocks and descriptions */}
      <div className="space-y-3">
        {recommendation.items.map((item, index) => {
          if (item.type === "course" && item.course) {
            return (
              <SelectableCourseCard
                key={`course-${item.course.id}-${index}`}
                course={item.course}
                onAddSection={onAddSection || (() => {})}
              />
            );
          } else if (item.type === "description" && item.description) {
            return (
              <div
                key={`desc-${index}`}
                className="text-sm text-gray-400 italic pl-2 border-l-2 border-gray-600"
              >
                {item.description}
              </div>
            );
          }
          return null;
        })}
      </div>

      {/* Dismiss button */}
      {onDismiss && (
        <div className="flex justify-end pt-2 border-t border-gray-700">
          <Button variant="ghost" size="sm" onClick={onDismiss}>
            Dismiss
          </Button>
        </div>
      )}
    </div>
  );
};

export default CourseRecommendation;
