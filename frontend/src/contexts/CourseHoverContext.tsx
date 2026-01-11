import { createContext, useContext, useState, ReactNode } from "react";
import type { Course, Section } from "@/components/SelectableCourseCard";

interface HoveredSection {
  section: Section;
  course: Course;
  index: number;
}

interface CourseHoverContextType {
  hoveredCourse: Course | null;
  setHoveredCourse: (course: Course | null) => void;
  hoveredSection: HoveredSection | null;
  setHoveredSection: (section: HoveredSection | null) => void;
}

const CourseHoverContext = createContext<CourseHoverContextType | undefined>(
  undefined
);

export const CourseHoverProvider = ({ children }: { children: ReactNode }) => {
  const [hoveredCourse, setHoveredCourse] = useState<Course | null>(null);
  const [hoveredSection, setHoveredSection] = useState<HoveredSection | null>(
    null
  );

  return (
    <CourseHoverContext.Provider
      value={{
        hoveredCourse,
        setHoveredCourse,
        hoveredSection,
        setHoveredSection,
      }}
    >
      {children}
    </CourseHoverContext.Provider>
  );
};

export const useCourseHover = () => {
  const context = useContext(CourseHoverContext);
  if (context === undefined) {
    throw new Error("useCourseHover must be used within a CourseHoverProvider");
  }
  return context;
};
