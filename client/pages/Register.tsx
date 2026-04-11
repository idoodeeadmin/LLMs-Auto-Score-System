import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Camera, Mail, User, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function Register() {
  const [isStudent, setIsStudent] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [avatarPreview, setAvatarPreview] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      toast.error("กรุณากรอกข้อมูลให้ครบถ้วน");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("รหัสผ่านไม่ตรงกัน");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          name,
          role: isStudent ? "student" : "teacher",
          student_id: isStudent ? studentId : null,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("ลงทะเบียนสำเร็จ กรุณาเข้าสู่ระบบ");
        navigate("/");
      } else {
        toast.error(data.detail || "เกิดข้อผิดพลาดในการลงทะเบียน");
      }
    } catch (error) {
      console.error("Register error:", error);
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

      {/* Right Side - Register Form */}
      <div className="flex-1 flex items-center justify-center bg-white px-6 sm:px-8 lg:px-12 py-8">
        <div className="w-full max-w-[540px]">
          {/* Back Button */}
          <Link
            to="/"
            className="inline-flex items-center text-black hover:text-[#3B82F6] transition-colors mb-6"
          >
            <ArrowLeft size={28} strokeWidth={2.5} />
          </Link>

          {/* Register Heading */}
          <div className="mb-8">
            <h1 className="text-[40px] font-bold text-black leading-tight mb-3">
              Register
            </h1>
            <p className="text-base text-black/60">
              Join our community of students and educators.
            </p>
          </div>

          {/* Role Toggle Buttons */}
          <div className="flex gap-3 mb-8">
            <button
              onClick={() => setIsStudent(true)}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-[20px] text-xl font-bold transition-all ${isStudent
                ? "bg-white border-2 border-[#3B82F6] text-[#3B82F6] shadow-[0_4px_4px_rgba(0,0,0,0.05)]"
                : "bg-transparent border-2 border-transparent text-[#B2B2B2]"
                }`}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.0001 5L12.0001 2L5.00006 5L8.50006 6.5V8.5M19.0001 5L15.5001 6.5V8.5M19.0001 5V9M8.50006 8.5C8.50006 8.5 9.66706 8 12.0001 8C14.3331 8 15.5001 8.5 15.5001 8.5M8.50006 8.5V9.5C8.50006 9.95963 8.59059 10.4148 8.76648 10.8394C8.94237 11.264 9.20018 11.6499 9.52519 11.9749C9.85019 12.2999 10.236 12.5577 10.6607 12.7336C11.0853 12.9095 11.5404 13 12.0001 13C12.4597 13 12.9148 12.9095 13.3395 12.7336C13.7641 12.5577 14.1499 12.2999 14.4749 11.9749C14.7999 11.6499 15.0577 11.264 15.2336 10.8394C15.4095 10.4148 15.5001 9.95963 15.5001 9.5V8.5M7.78306 16.703C6.68306 17.388 3.79706 18.785 5.55406 20.534C6.41306 21.39 7.37006 22 8.57106 22H15.4291C16.6311 22 17.5871 21.389 18.4461 20.534C20.2031 18.785 17.3181 17.388 16.2171 16.704C14.9511 15.9174 13.4905 15.5005 12.0001 15.5005C10.5097 15.5005 9.04897 15.9174 7.78306 16.704" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              I am a Student
            </button>

            <button
              onClick={() => setIsStudent(false)}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-[20px] text-xl font-bold transition-all ${!isStudent
                ? "bg-white border-2 border-[#3B82F6] text-[#3B82F6] shadow-[0_4px_4px_rgba(0,0,0,0.05)]"
                : "bg-transparent border-2 border-transparent text-[#B2B2B2]"
                }`}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 17C20.5304 17 21.0391 16.7893 21.4142 16.4142C21.7893 16.0391 22 15.5304 22 15V4C22 3.46957 21.7893 2.96086 21.4142 2.58579C21.0391 2.21071 20.5304 2 20 2H9.46C9.81 2.61 10 3.3 10 4H20V15H11V17M15 7V9H9V22H7V16H5V22H3V14H1.5V9C1.5 8.46957 1.71071 7.96086 2.08579 7.58579C2.46086 7.21071 2.96957 7 3.5 7H15ZM8 4C8 4.53043 7.78929 5.03914 7.41421 5.41421C7.03914 5.78929 6.53043 6 6 6C5.46957 6 4.96086 5.78929 4.58579 5.41421C4.21071 5.03914 4 4.53043 4 4C4 3.46957 4.21071 2.96086 4.58579 2.58579C4.96086 2.21071 5.46957 2 6 2C6.53043 2 7.03914 2.21071 7.41421 2.58579C7.78929 2.96086 8 3.46957 8 4Z" fill="currentColor" />
              </svg>
              I am a Teacher
            </button>
          </div>

          <form onSubmit={handleRegister}>
            {/* Avatar Upload */}
            <div className="flex justify-center mb-8">
              <div className="relative">
                <label htmlFor="avatar-upload" className="cursor-pointer">
                  <div className="w-24 h-24 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors overflow-hidden">
                    {avatarPreview ? (
                      <img
                        src={avatarPreview}
                        alt="Avatar preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <User size={40} className="text-gray-400" />
                    )}
                  </div>
                  <div className="absolute bottom-0 right-0 w-8 h-8 bg-[#3B82F6] rounded-full flex items-center justify-center shadow-md">
                    <Camera size={18} className="text-white" />
                  </div>
                </label>
                <input
                  id="avatar-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                />
              </div>
            </div>

            {/* Name Input */}
            <div className="mb-6">
              <label className="block text-lg font-medium text-black mb-2">
                Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter name"
                required
                className="w-full px-5 py-3.5 text-lg font-normal text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
              />
            </div>

            {/* Email Input */}
            <div className="mb-6">
              <label className="block text-lg font-medium text-black mb-2">
                Email Address
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                  className="w-full px-5 py-3.5 pl-12 text-lg font-normal text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
                <Mail
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-black"
                  size={20}
                />
              </div>
            </div>

            {/* Student ID Input */}
            {isStudent && (
              <div className="mb-6">
                <label className="block text-lg font-medium text-black mb-2">
                  Student ID
                </label>
                <input
                  type="text"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  placeholder="Enter your student ID"
                  required={isStudent}
                  className="w-full px-5 py-3.5 text-lg font-normal text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
              </div>
            )}

            {/* Password Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
              <div>
                <label className="block text-lg font-medium text-black mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full px-5 py-3.5 text-lg font-normal text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
              </div>
              <div>
                <label className="block text-lg font-medium text-black mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full px-5 py-3.5 text-lg font-normal text-black placeholder:text-[#C9C9C9] rounded-[20px] border-[1.5px] border-[#C9C9C9] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] focus:outline-none focus:border-[#3B82F6] transition-colors"
                />
              </div>
            </div>

            {/* Register Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 text-2xl font-medium text-white bg-[#3B82F6] rounded-[20px] shadow-[0_4px_4px_rgba(0,0,0,0.05)] hover:bg-[#2563EB] transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center font-bold"
            >
              {isLoading ? <Loader2 className="animate-spin mr-2" /> : "Register"}
            </button>
          </form>

          {/* Mobile Logo - Show on smaller screens */}
          <div className="lg:hidden mt-8 flex flex-col items-center">
            <img
              src="https://api.builder.io/api/v1/image/assets/TEMP/eb4441680ef793285669451cd4b222e32d202205?width=568"
              alt="Evaly Logo"
              className="w-24 h-24 opacity-90"
            />
            <h2 className="text-xl font-medium text-gray-700 mt-2">Evaly</h2>
          </div>
        </div>
      </div>
    </div>
  );
}
