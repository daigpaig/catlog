import AboutMe from "@/components/AboutMe";
import HeaderBar from "@/components/HeaderBar";
import SchedulingPreferences from "@/components/SchedulingPreferences";
import React, { useEffect, useState } from "react";
import { apiService } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";

interface UserProfile {
  netid: string;
  name: string;
  email: string;
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

const Profile = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await apiService.get<UserProfile>("/profile/me");
        setProfile(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col">
        <div className="fixed top-0 w-full z-50">
          <HeaderBar />
        </div>
        <div className="bg-[#1f0724] p-8 h-full flex items-center justify-center text-white pt-32">
          <div>Loading profile...</div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="flex flex-col">
        <div className="fixed top-0 w-full z-50">
          <HeaderBar />
        </div>
        <div className="bg-[#1f0724] p-8 h-full flex items-center justify-center text-white pt-32">
          <div className="text-red-400">Error: {error || "Profile not found"}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <div className="fixed top-0 w-full z-50">
        <HeaderBar />
      </div>
      <div className="bg-[#1f0724] p-8 h-full flex flex-col gap-1 text-white overflow-auto pt-32">
        <h1 className="text-3xl font-bold">{profile.name}</h1>
        <h2 className="text-xl font-light text-gray-300">{profile.netid}</h2>
        <AboutMe
          netid={profile.netid}
          full_name={profile.name}
          majors={profile.majors}
          minors={profile.minors || []}
          classes_already_taken={profile.classes_already_taken || []}
          vocational_interests={profile.vocational_interests || []}
          favorite_profs={profile.favorite_profs || []}
          disliked_profs={profile.disliked_profs || []}
          earliest_class_time={profile.earliest_class_time || ""}
          locked_classes={profile.locked_classes || []}
        />
        <SchedulingPreferences />
      </div>
    </div>
  );
};

export default Profile;
