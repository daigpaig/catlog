import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { apiService } from "@/services/api";
import type { Schedule } from "@/types/api";

interface ScheduleContextType {
  schedules: Schedule[];
  selectedScheduleId: number | null;
  setSelectedScheduleId: (id: number | null) => void;
  refreshSchedules: () => Promise<void>;
  loading: boolean;
}

const ScheduleContext = createContext<ScheduleContextType | undefined>(undefined);

export const ScheduleProvider = ({ children }: { children: ReactNode }) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [selectedScheduleId, setSelectedScheduleId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshSchedules = async () => {
    try {
      const fetchedSchedules = await apiService.getSchedules();
      setSchedules(fetchedSchedules);
      if (fetchedSchedules.length > 0 && !selectedScheduleId) {
        setSelectedScheduleId(fetchedSchedules[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch schedules:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSchedules();
  }, []);

  return (
    <ScheduleContext.Provider
      value={{
        schedules,
        selectedScheduleId,
        setSelectedScheduleId,
        refreshSchedules,
        loading,
      }}
    >
      {children}
    </ScheduleContext.Provider>
  );
};

export const useSchedule = () => {
  const context = useContext(ScheduleContext);
  if (context === undefined) {
    throw new Error("useSchedule must be used within a ScheduleProvider");
  }
  return context;
};
