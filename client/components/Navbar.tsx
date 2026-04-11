import { Bell, User, LogOut, Settings, UserCircle } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";

interface NavbarProps {
  activeTab?: string;
  setActiveTab?: (tab: any) => void;
}

export default function Navbar({ }: NavbarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="bg-white border-b border-gray-100 px-4 md:px-6 py-3 md:py-4 sticky top-0 z-50 shadow-sm backdrop-blur-md bg-white/90">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
        {/* Logo (Links to dashboard/home) */}
        <Link to="/home" className="flex items-center gap-2 md:gap-3 flex-shrink-0 group">
          <div className="w-10 h-10 md:w-12 md:h-12 bg-[#eff6ff] rounded-2xl flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19.0001 5L12.0001 2L5.00006 5L8.50006 6.5V8.5M19.0001 5L15.5001 6.5V8.5M19.0001 5V9M8.50006 8.5C8.50006 8.5 9.66706 8 12.0001 8C14.3331 8 15.5001 8.5 15.5001 8.5M8.50006 8.5V9.5C8.50006 9.95963 8.59059 10.4148 8.76648 10.8394C8.94237 11.264 9.20018 11.6499 9.52519 11.9749C9.85019 12.2999 10.236 12.5577 10.6607 12.7336C11.0853 12.9095 11.5404 13 12.0001 13C12.4597 13 12.9148 12.9095 13.3395 12.7336C13.7641 12.5577 14.1499 12.2999 14.4749 11.9749C14.7999 11.6499 15.0577 11.264 15.2336 10.8394C15.4095 10.4148 15.5001 9.95963 15.5001 9.5V8.5M7.78306 16.703C6.68306 17.388 3.79706 18.785 5.55406 20.534C6.41306 21.39 7.37006 22 8.57106 22H15.4291C16.6311 22 17.5871 21.389 18.4461 20.534C20.2031 18.785 17.3181 17.388 16.2171 16.704C14.9511 15.9174 13.4905 15.5005 12.0001 15.5005C10.5097 15.5005 9.04897 15.9174 7.78306 16.704" stroke="#3B82F6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <h1 className="text-xl md:text-2xl font-black text-gray-900 tracking-tight">Evaly</h1>
        </Link>

        {/* Right side icons */}
        <div className="flex items-center gap-3 md:gap-5 ml-auto">
          <button className="p-2 hover:bg-gray-100 rounded-full transition-colors relative">
            <Bell size={22} className="text-gray-600 md:w-6 md:h-6" />
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full"></span>
          </button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="w-9 h-9 md:w-11 md:h-11 bg-[#eff6ff] border border-blue-100 rounded-full flex items-center justify-center hover:bg-blue-100 transition-colors shadow-sm focus:ring-2 focus:ring-blue-400 focus:outline-none overflow-hidden">
                <User size={18} className="text-[#3B82F6] md:w-5 md:h-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 rounded-xl mt-1 shadow-lg border-gray-100 p-2">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-bold leading-none">{user?.name}</p>
                  <p className="text-xs leading-none text-gray-500 uppercase">
                    {user?.role === 'teacher' ? 'อาจารย์' : 'นักศึกษา'}
                  </p>
                  <p className="text-xs leading-none text-gray-400">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-50 my-2" />
              <DropdownMenuItem className="rounded-lg gap-2 cursor-pointer focus:bg-blue-50 focus:text-blue-600">
                <UserCircle size={18} />
                <span>ข้อมูลส่วนตัว</span>
              </DropdownMenuItem>
              <DropdownMenuItem className="rounded-lg gap-2 cursor-pointer focus:bg-blue-50 focus:text-blue-600">
                <Settings size={18} />
                <span>การตั้งค่า</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-50 my-2" />
              <DropdownMenuItem 
                onClick={handleLogout}
                className="rounded-lg gap-2 cursor-pointer text-red-500 focus:bg-red-50 focus:text-red-600 font-medium"
              >
                <LogOut size={18} />
                <span>ออกจากระบบ</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}