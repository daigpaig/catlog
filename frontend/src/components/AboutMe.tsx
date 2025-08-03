import React from "react";
import { Pencil } from "lucide-react";

interface ProfileProps {
  netid: string;
  full_name: string;
  majors: string[];
  minors?: string[];
  classes_already_taken?: string[];
  vocational_interests?: string[];
  favorite_profs?: string[];
  disliked_profs?: string[];
  earliest_class_time?: string;
  locked_classes?: string[];
  self_description?: string;
}

const AboutMe = ({
  netid,
  full_name,
  majors,
  minors,
  vocational_interests,
  favorite_profs,
  disliked_profs,
  self_description,
}: ProfileProps) => {
  const categoryLabels = {
    "Major(s)": majors,
    "Minor(s)": minors,
    "Vocational Interests": vocational_interests,
    "Favorite Professors": favorite_profs,
    "Professors to avoid": disliked_profs,
    "Self description": self_description,
  };
  return (
    <div className="overflow-auto h-full bg-[#301934] rounded-lg p-4 my-3">
      <h2 className="text-lg font-bold">About Me</h2>
      <p>
        Catlog AI suggests classes based on your majors, minors, vocational
        interests, favorite professors, and more. Provide as much information as
        you can here to get better suggestions.
      </p>
      <div className="grid grid-cols-3 gap-4 my-3">
        {Object.entries(categoryLabels).map(([label, value]) => (
          <button
            key={label}
            className="bg-gray-800 hover:bg-gray-600 hover:cursor-pointer p-5 rounded-md m-1 flex min-w-1/3 group justify-between"
          >
            <div className="flex flex-col text-left">
              <p className="font-bold">{label}</p>
              <p>{Array.isArray(value) ? value.join(", ") : value}</p>
            </div>
            <Pencil className="opacity-0 group-hover:opacity-100 h-5" />
          </button>
        ))}
      </div>
    </div>
  );
};

export default AboutMe;
