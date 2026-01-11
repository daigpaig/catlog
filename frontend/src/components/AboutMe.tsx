import React, { useState } from "react";
import { Pencil, Check, X } from "lucide-react";
import { Combobox } from "@/components/ui/combobox";
import { apiService } from "@/services/api";

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
  onUpdate?: () => void; // Callback to refresh profile after update
  // Full profile data for updates - need all fields for backend
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
  };
}

// Sample options - will be expanded later
const MAJOR_OPTIONS = [
  "Computer Science",
  "Mathematics",
  "Statistics",
  "Economics",
  "Psychology",
  "Political Science",
  "History",
  "English",
  "Biology",
  "Chemistry",
  "Physics",
  "Engineering",
  "Business",
  "Communications",
  "Journalism",
];

const MINOR_OPTIONS = [
  "Computer Science",
  "Mathematics",
  "Statistics",
  "Economics",
  "Psychology",
  "Political Science",
  "History",
  "English",
  "Biology",
  "Chemistry",
  "Physics",
  "Engineering",
  "Business",
  "Communications",
  "Journalism",
  "Data Science",
  "Linguistics",
  "Philosophy",
];

const VOCATIONAL_INTERESTS_OPTIONS = [
  "Software Engineering",
  "Data Science",
  "Research",
  "Education",
  "Finance",
  "Consulting",
  "Healthcare",
  "Law",
  "Marketing",
  "Entrepreneurship",
  "Non-profit",
  "Government",
  "Media",
  "Design",
  "Engineering",
];

const PROFESSOR_OPTIONS = [
  "Professor Smith",
  "Professor Johnson",
  "Professor Williams",
  "Professor Brown",
  "Professor Jones",
  "Professor Garcia",
  "Professor Miller",
  "Professor Davis",
  "Professor Rodriguez",
  "Professor Martinez",
];

interface EditableFieldProps {
  label: string;
  value: string[] | string | undefined;
  isEditing: boolean;
  onStartEdit: () => void;
  onSave: (newValue: string[] | string) => void;
  onCancel: () => void;
  fieldType: "combobox" | "textarea";
  options?: string[];
  placeholder?: string;
}

const EditableField: React.FC<EditableFieldProps> = ({
  label,
  value,
  isEditing,
  onStartEdit,
  onSave,
  onCancel,
  fieldType,
  options = [],
  placeholder,
}) => {
  const [tempValue, setTempValue] = useState<string[] | string>(
    value || (fieldType === "combobox" ? [] : "")
  );

  React.useEffect(() => {
    setTempValue(value || (fieldType === "combobox" ? [] : ""));
  }, [value, fieldType]);

  const handleSave = () => {
    onSave(tempValue);
  };

  const handleCancel = () => {
    setTempValue(value || (fieldType === "combobox" ? [] : ""));
    onCancel();
  };

  const displayValue =
    fieldType === "combobox"
      ? Array.isArray(value) && value.length > 0
        ? value.join(", ")
        : placeholder || "None selected"
      : value || placeholder || "Click to add...";

  return (
    <div className="bg-gray-800 hover:bg-gray-700 rounded-md p-4 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <p className="font-bold text-white">{label}</p>
        {!isEditing && (
          <button
            onClick={onStartEdit}
            className="opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity p-1 hover:bg-gray-600 rounded"
            title="Edit"
          >
            <Pencil className="h-4 w-4 text-gray-300 hover:text-white" />
          </button>
        )}
      </div>

      {!isEditing ? (
        <p className="text-gray-300 text-sm min-h-[1.5rem]">
          {displayValue}
        </p>
      ) : (
        <div className="space-y-3">
          {fieldType === "combobox" ? (
            <Combobox
              options={options}
              values={Array.isArray(tempValue) ? tempValue : []}
              onChange={(newValues) => setTempValue(newValues)}
              placeholder={placeholder || `Select ${label.toLowerCase()}...`}
            />
          ) : (
            <textarea
              value={typeof tempValue === "string" ? tempValue : ""}
              onChange={(e) => setTempValue(e.target.value)}
              className="w-full bg-gray-900 border border-gray-600 rounded-md px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-gray-500 resize-none"
              rows={4}
              placeholder={placeholder || `Enter ${label.toLowerCase()}...`}
            />
          )}
          <div className="flex gap-2 justify-end">
            <button
              onClick={handleCancel}
              className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
            <button
              onClick={handleSave}
              className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              <Check className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const AboutMe = ({
  netid,
  full_name,
  majors,
  minors = [],
  vocational_interests = [],
  favorite_profs = [],
  disliked_profs = [],
  self_description = "",
  onUpdate,
  fullProfile,
}: ProfileProps) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [localProfile, setLocalProfile] = useState({
    majors,
    minors,
    vocational_interests,
    favorite_profs,
    disliked_profs,
    self_description,
  });
  const [saving, setSaving] = useState(false);

  // Update local profile when props change
  React.useEffect(() => {
    setLocalProfile({
  majors,
  minors,
  vocational_interests,
  favorite_profs,
  disliked_profs,
  self_description,
    });
  }, [majors, minors, vocational_interests, favorite_profs, disliked_profs, self_description]);

  const handleSave = async (
    field: string,
    newValue: string[] | string
  ) => {
    setSaving(true);
    try {
      const updatedProfile = {
        ...localProfile,
        [field]: newValue,
      };
      
      // Use fullProfile as base to ensure we send all required fields
      const baseProfile = fullProfile || {
        netid,
        majors: majors || [],
        minors: minors || [],
        classes_already_taken: [],
        vocational_interests: [],
        favorite_profs: [],
        disliked_profs: [],
        earliest_class_time: undefined,
        locked_classes: [],
        self_description: "",
      };
      
      // Send all fields, overriding only the edited field
      await apiService.updateProfile({
        netid: baseProfile.netid,
        majors: updatedProfile.majors || baseProfile.majors || [],
        minors: updatedProfile.minors || baseProfile.minors || [],
        classes_already_taken: baseProfile.classes_already_taken || [],
        vocational_interests: updatedProfile.vocational_interests || baseProfile.vocational_interests || [],
        favorite_profs: updatedProfile.favorite_profs || baseProfile.favorite_profs || [],
        disliked_profs: updatedProfile.disliked_profs || baseProfile.disliked_profs || [],
        earliest_class_time: baseProfile.earliest_class_time,
        locked_classes: baseProfile.locked_classes || [],
        self_description: updatedProfile.self_description !== undefined ? updatedProfile.self_description : (baseProfile.self_description || ""),
      });

      setLocalProfile(updatedProfile);
      setEditingField(null);
      
      // Refresh profile in parent component
      if (onUpdate) {
        onUpdate();
      }
    } catch (error) {
      console.error("Failed to update profile:", error);
      alert("Failed to update profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const fields = [
    {
      key: "majors",
      label: "Major(s)",
      value: localProfile.majors,
      type: "combobox" as const,
      options: MAJOR_OPTIONS,
    },
    {
      key: "minors",
      label: "Minor(s)",
      value: localProfile.minors,
      type: "combobox" as const,
      options: MINOR_OPTIONS,
    },
    {
      key: "vocational_interests",
      label: "Vocational Interests",
      value: localProfile.vocational_interests,
      type: "combobox" as const,
      options: VOCATIONAL_INTERESTS_OPTIONS,
    },
    {
      key: "favorite_profs",
      label: "Favorite Professors",
      value: localProfile.favorite_profs,
      type: "combobox" as const,
      options: PROFESSOR_OPTIONS,
    },
    {
      key: "disliked_profs",
      label: "Professors to avoid",
      value: localProfile.disliked_profs,
      type: "combobox" as const,
      options: PROFESSOR_OPTIONS,
    },
    {
      key: "self_description",
      label: "Self description",
      value: localProfile.self_description,
      type: "textarea" as const,
      options: undefined,
    },
  ];

  return (
    <div className="overflow-auto h-full bg-[#301934] rounded-lg p-4 my-3 text-white">
      <h2 className="text-lg font-bold mb-2">About Me</h2>
      <p className="text-gray-300 text-sm mb-4">
        Catlog AI suggests classes based on your majors, minors, vocational
        interests, favorite professors, and more. Provide as much information as
        you can here to get better suggestions.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {fields.map((field) => (
          <div key={field.key} className="group">
            <EditableField
              label={field.label}
              value={field.value}
              isEditing={editingField === field.key}
              onStartEdit={() => setEditingField(field.key)}
              onSave={(newValue) => handleSave(field.key, newValue)}
              onCancel={() => setEditingField(null)}
              fieldType={field.type}
              options={field.options}
              placeholder={`Add ${field.label.toLowerCase()}...`}
            />
            </div>
        ))}
      </div>
      {saving && (
        <div className="mt-4 text-sm text-gray-400">Saving...</div>
      )}
    </div>
  );
};

export default AboutMe;
