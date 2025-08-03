import React from "react";
import icon from "@/assets/icon.svg";
import { LucideMenu } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Link } from "react-router-dom";

const HeaderBar = () => {
  return (
    <div className="flex items-center justify-between bg-[#1f0724] border-b border-gray-500 px-4 py-2">
      <div className="flex items-center space-x-3">
        <img src={icon} alt="Logo" className="w-22" />
        <h1 className="align-middle text-white text-3xl">Catlog</h1>
      </div>
      <DropdownMenu>
        <DropdownMenuTrigger className="mx-3 hover:cursor-pointer">
          <LucideMenu className="h-7 w-7 text-white" />
        </DropdownMenuTrigger>
        <DropdownMenuContent className="bg-gray-700 opacity-75 mx-3 text-white">
          <Link to="/profile">
            <DropdownMenuItem>My Profile</DropdownMenuItem>
          </Link>
          <DropdownMenuItem>About Catlog</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

export default HeaderBar;
