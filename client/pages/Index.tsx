import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Eye, EyeOff, Mail, Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

export default function Index() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("กรุณากรอกอีเมลและรหัสผ่าน");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        login(data.access_token, data.user);
        navigate("/home");
      } else {
        toast.error(data.detail || "อีเมลหรือรหัสผ่านไม่ถูกต้อง");
      }
    } catch (error) {
      console.error("Login error:", error);
      toast.error("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Side - Dark Background with Image */}
      <div className="relative hidden lg:flex lg:w-1/2 bg-gradient-to-b from-[#2F3B48] to-[#445468] items-center justify-center overflow-hidden">
        {/* Background Image */}
        <img
          src="https://api.builder.io/api/v1/image/assets/TEMP/91e324bc3ea2042ded0899862fcec54022cda24a?width=1584"
          alt="Study desk with books"
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Logo Icon */}
        <div className="relative z-10 flex flex-col items-center">
          <img
            src="https://api.builder.io/api/v1/image/assets/TEMP/eb4441680ef793285669451cd4b222e32d202205?width=568"
            alt="Evaly Logo"
            className="w-[284px] h-[284px] opacity-90"
          />
          <h1 className="text-white text-[40px] font-medium mt-[-30px] drop-shadow-[0_4px_4px_rgba(0,0,0,0.25)]">
            Evaly
          </h1>
        </div>

        {/* Bottom Text */}
        <div className="absolute bottom-[110px] left-[37px] text-white">
          <h2 className="text-2xl font-bold">LLM-AutoScore</h2>
          <p className="text-base mt-1">ข้อสอบคุณเราตรวจเอง</p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center bg-white px-6 sm:px-8 lg:px-12">
        <div className="w-full max-w-[540px]">
          {/* Welcome Text */}
          <div className="text-center lg:text-left mb-12">
            <h1 className="text-[40px] font-bold text-black leading-tight">
              Welcome Back
            </h1>
            <p className="text-[15px] text-black/43 mt-4">
              Please enter your details to access the Evaly.
            </p>
          </div>

          <form onSubmit={handleLogin}>
            {/* Email Input */}
            <div className="mb-6">
              <label className="block text-2xl font-medium text-black mb-3">
                Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter yor email"
                  required
                  className="w-full px-5 py-4 pr-14 text-2xl font-medium text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-[rgba(235,234,234,0.50)] shadow-[0_4px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
                <Mail
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-[#C9C9C9]"
                  size={24}
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <label className="text-2xl font-medium text-black">
                  Password
                </label>
                <a
                  href="#"
                  className="text-xl font-medium text-[#3B82F6] hover:underline"
                >
                  forgot Password?
                </a>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter yor password"
                  required
                  className="w-full px-5 py-4 pr-14 text-2xl font-medium text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-[rgba(235,234,234,0.50)] shadow-[0_4px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-5 top-1/2 -translate-y-1/2 text-[#C9C9C9] hover:text-[#3B82F6] transition-colors"
                >
                  {showPassword ? <Eye size={24} /> : <EyeOff size={24} />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 text-2xl font-medium text-white bg-[#3B82F6] rounded-[20px] shadow-[0_4px_4px_rgba(0,0,0,0.05)] hover:bg-[#2563EB] transition-colors mb-4 flex items-center justify-center disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? <Loader2 className="animate-spin mr-2" /> : "Login"}
            </button>
          </form>

          {/* Register Button */}
          <Link
            to="/register"
            className="w-full py-3 text-2xl font-medium text-white bg-[rgba(255,88,88,0.79)] rounded-[20px] shadow-[0_4px_4px_rgba(0,0,0,0.05)] hover:bg-[rgba(255,88,88,0.9)] transition-colors flex items-center justify-center"
          >
            Register
          </Link>

          {/* Mobile Logo - Show on smaller screens */}
          <div className="lg:hidden mt-12 flex flex-col items-center">
            <img
              src="https://api.builder.io/api/v1/image/assets/TEMP/eb4441680ef793285669451cd4b222e32d202205?width=568"
              alt="Evaly Logo"
              className="w-32 h-32 opacity-90"
            />
            <h2 className="text-2xl font-medium text-gray-700 mt-2">Evaly</h2>
          </div>
        </div>
      </div>
    </div>
  );
}
