import AboutMe from "@/components/AboutMe";
import HeaderBar from "@/components/HeaderBar";
import SchedulingPreferences from "@/components/SchedulingPreferences";
import React from "react";

const sampleProfile = {
  netid: "wpe1403",
  full_name: "Daigo Moriwake",
  majors: ["Data Science"],
  minors: ["Italian", "Transportation & Logistics"],
  classes_already_taken: ["STAT 303-3", "MATH 240"],
  vocational_interests: ["NLP", "Transportation Modeling"],
  favorite_profs: ["Voigt", "Besler"],
  disliked_profs: [],
  earliest_class_time: "10:00",
  locked_classes: ["CS214"],
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
