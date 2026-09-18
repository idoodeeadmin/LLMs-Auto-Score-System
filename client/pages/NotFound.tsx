import { Link, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { ArrowLeft, SearchX } from "lucide-react";
import { Button } from "@/components/ui/button";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6 dark:bg-slate-950">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <span className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
          <SearchX size={26} />
        </span>
        <p className="mb-2 text-sm font-semibold text-emerald-700 dark:text-emerald-300">ข้อผิดพลาด 404</p>
        <h1 className="mb-3 text-2xl font-semibold text-slate-950 dark:text-white">ไม่พบหน้าที่คุณต้องการ</h1>
        <p className="mb-6 text-sm leading-6 text-slate-500 dark:text-slate-400">ลิงก์นี้อาจถูกย้ายหรือพิมพ์ไม่ถูกต้อง กลับไปยังหน้าหลักเพื่อเลือกเส้นทางอีกครั้ง</p>
        <Button asChild className="primary-action w-full">
          <Link to="/"><ArrowLeft className="mr-2 h-4 w-4" /> กลับหน้าเข้าสู่ระบบ</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
