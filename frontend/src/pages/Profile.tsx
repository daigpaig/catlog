import AboutMe from "@/components/AboutMe";
import HeaderBar from "@/components/HeaderBar";
import SchedulingPreferences from "@/components/SchedulingPreferences";
import React from "react";

const sampleProfile = {
  netid: "student",
  full_name: "Student Profile",
  majors: ["Computer Science"],
  minors: ["Mathematics"],
  classes_already_taken: ["CS 101", "MATH 220"],
  vocational_interests: ["Software Engineering", "Data Analysis"],
  favorite_profs: [],
  disliked_profs: [],
  earliest_class_time: "09:00",
  locked_classes: [],
};

const Profile = () => {
  return (
    <div className="flex flex-col">
      <div className="fixed top-0 w-full z-50">
        <HeaderBar />
      </div>
      <div className="bg-[#1f0724] p-8 h-full flex flex-col gap-1 text-white overflow-auto pt-32">
        <h1 className="text-3xl font-bold">{sampleProfile.full_name}</h1>
        <h2 className="text-xl font-light text-gray-300">
          {sampleProfile.netid}
        </h2>
        <AboutMe {...sampleProfile} />
        <SchedulingPreferences />
      </div>
    </div>
  );
};

export default Profile;
