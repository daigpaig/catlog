import { useState, useEffect, useRef } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiService } from "@/services/api";
import type { Schedule } from "@/types/api";

interface CreateScheduleModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: (schedule: Schedule) => void;
  existingSchedules: Schedule[];
}

const CreateScheduleModal = ({
  open,
  onOpenChange,
  onSuccess,
  existingSchedules,
}: CreateScheduleModalProps) => {
  const [name, setName] = useState("");
  const [term, setTerm] = useState("");
  const [nameError, setNameError] = useState("");
  const [termError, setTermError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const nameInputRef = useRef<HTMLInputElement>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (open) {
      setName("");
      setTerm("");
      setNameError("");
      setTermError("");
      // Focus the name input when modal opens
      setTimeout(() => {
        nameInputRef.current?.focus();
      }, 100);
    }
  }, [open]);

  const validateForm = (): boolean => {
    let isValid = true;

    // Validate name
    if (!name.trim()) {
      setNameError("Schedule name is required");
      isValid = false;
    } else if (existingSchedules.some((s) => s.name.toLowerCase() === name.trim().toLowerCase())) {
      setNameError("A schedule with this name already exists");
      isValid = false;
    } else {
      setNameError("");
    }

    // Validate term
    if (!term.trim()) {
      setTermError("Term is required");
      isValid = false;
    } else {
      setTermError("");
    }

    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const newSchedule = await apiService.createSchedule({
        name: name.trim(),
        term: term.trim(),
      });
      
      // Call success callback with the created schedule
      onSuccess(newSchedule);
      
      // Close modal
      onOpenChange(false);
    } catch (error) {
      console.error("Failed to create schedule:", error);
      // You could add error state here to show in the modal
      setTermError("Failed to create schedule. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Close on Escape
    if (e.key === "Escape") {
      handleCancel();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        onKeyDown={handleKeyDown}
        className="bg-gray-900 border-gray-700 text-white"
      >
        <DialogHeader>
          <DialogTitle className="text-white">Create New Schedule</DialogTitle>
          <DialogDescription className="text-gray-400">
            Enter a name and term for your new schedule.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label
                htmlFor="schedule-name"
                className="text-sm font-medium text-gray-300"
              >
                Schedule Name
              </label>
              <Input
                id="schedule-name"
                ref={nameInputRef}
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (nameError) setNameError("");
                }}
                placeholder="e.g., Spring 2025"
                className={nameError ? "border-red-500" : ""}
                aria-invalid={!!nameError}
                aria-describedby={nameError ? "name-error" : undefined}
              />
              {nameError && (
                <p
                  id="name-error"
                  className="text-sm text-red-400"
                  role="alert"
                >
                  {nameError}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <label
                htmlFor="schedule-term"
                className="text-sm font-medium text-gray-300"
              >
                Term
              </label>
              <Input
                id="schedule-term"
                value={term}
                onChange={(e) => {
                  setTerm(e.target.value);
                  if (termError) setTermError("");
                }}
                placeholder="e.g., Fall 2025"
                className={termError ? "border-red-500" : ""}
                aria-invalid={!!termError}
                aria-describedby={termError ? "term-error" : undefined}
              />
              {termError && (
                <p
                  id="term-error"
                  className="text-sm text-red-400"
                  role="alert"
                >
                  {termError}
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isSubmitting}
              className="bg-gray-800 text-white border-gray-700 hover:bg-gray-700"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-purple-600 text-white hover:bg-purple-700"
            >
              {isSubmitting ? "Creating..." : "Create Schedule"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateScheduleModal;

