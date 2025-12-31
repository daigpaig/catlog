import React from "react";
import icon from "@/assets/icon.svg";
import { LucideMenu } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const HeaderBar = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex items-center justify-between bg-[#1f0724] border-b border-gray-500 px-4 py-2">
      <div className="flex items-center space-x-3">
        <img src={icon} alt="Logo" className="w-22" />
        <h1 className="align-middle text-white text-3xl">Catlog</h1>
      </div>
      <div className="flex items-center space-x-4">
        {user && (
          <span className="text-white text-sm">{user.name || user.email}</span>
        )}
        <DropdownMenu>
          <DropdownMenuTrigger className="mx-3 hover:cursor-pointer">
            <LucideMenu className="h-7 w-7 text-white" />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-700 opacity-75 mx-3 text-white">
            <Link to="/profile">
              <DropdownMenuItem>My Profile</DropdownMenuItem>
            </Link>
            <DropdownMenuItem>About Catlog</DropdownMenuItem>
            <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

export default HeaderBar;
