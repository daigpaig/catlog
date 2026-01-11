import { Button } from "@/components/ui/button";
import SelectableCourseCard from "./SelectableCourseCard";
import type { Course } from "./SelectableCourseCard";

export interface MultiCourseRecommendationData {
  id?: string;
  title?: string;
  rationale: string;
  courses: Course[];
  priority?: "high" | "medium" | "low";
}

interface MultiCourseRecommendationProps {
  recommendation: MultiCourseRecommendationData;
  onAddSection?: (sectionId: string, course: Course, section: import("./SelectableCourseCard").Section) => void;
  onDismiss?: () => void;
}

const MultiCourseRecommendation = ({
  recommendation,
  onAddSection,
  onDismiss,
}: MultiCourseRecommendationProps) => {

  // Safety check: don't render if no courses
  if (!recommendation.courses || recommendation.courses.length === 0) {
    return (
      <div className="rounded-2xl border border-gray-700 bg-gray-800/50 p-4">
        <p className="text-sm text-gray-400">
          No courses found in this recommendation.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-gray-700 bg-gray-800/50 p-4 space-y-3">
      {/* Title (optional) */}
      {recommendation.title && (
        <h3 className="text-lg font-semibold text-white">
          {recommendation.title}
        </h3>
      )}

      {/* Priority badge */}
      {recommendation.priority && (
        <div
          className={`inline-block px-2 py-1 text-xs rounded ${
            recommendation.priority === "high"
              ? "bg-red-500/20 text-red-300"
              : recommendation.priority === "medium"
              ? "bg-yellow-500/20 text-yellow-300"
              : "bg-blue-500/20 text-blue-300"
          }`}
        >
          {recommendation.priority} priority
        </div>
      )}

      {/* Rationale */}
      <p className="text-sm text-gray-300 leading-relaxed">
        {recommendation.rationale}
      </p>

      {/* Course list */}
      <div className="space-y-2">
        {(recommendation.courses || []).map((course) => (
          <SelectableCourseCard
            key={course.id}
            course={course}
            onAddSection={onAddSection || (() => {})}
          />
        ))}
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

export default MultiCourseRecommendation;
