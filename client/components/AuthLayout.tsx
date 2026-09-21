import type { ReactNode } from "react";
import economicsHero from "@/assets/economics-classroom-hero-v4.png";
import { ThemeToggle } from "@/components/ThemeToggle";

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="workspace auth-workspace flex min-h-screen">
      <section className="relative hidden min-h-screen w-1/2 overflow-hidden bg-[#203c32] lg:flex">
        <img src={economicsHero} alt="ชั้นเรียนเศรษฐศาสตร์และการเรียนการสอน" className="absolute inset-0 h-full w-full object-cover object-[55%_center] brightness-[0.92] saturate-[0.82]" />
        <div className="absolute inset-0 bg-gradient-to-b from-[#062c25]/65 via-[#0c4a3e]/25 to-[#062c25]/95" />
        <div className="relative z-10 flex w-full flex-col justify-between p-12 xl:p-16">
          <div className="workspace-brand text-white">Evaly <span className="border-white/20 text-white/70">พื้นที่การสอบ</span></div>
          <div className="max-w-[380px] text-white">
            <p className="mb-4 text-sm font-medium text-white/80">พื้นที่การสอบสำหรับชั้นเรียนของคุณ</p>
            <h1 className="max-w-[380px] text-4xl font-semibold leading-[1.18] tracking-tight">
              สร้างชั้นเรียน
              <br />
              และจัดการข้อสอบในที่เดียว
            </h1>
            <p className="mt-5 max-w-[380px] text-base leading-7 text-white/80">
              สร้างห้องเรียน เชิญผู้เรียน มอบหมายข้อสอบ และติดตามคะแนนได้ง่าย
              ในพื้นที่เดียว
            </p>
          </div>
          <p className="text-xs text-white/60">Evaly Score · Exam workspace</p>
        </div>
      </section>


      <main className="relative flex min-h-screen w-full flex-1 items-center justify-center px-6 py-20 sm:px-10 lg:w-1/2 lg:px-16">
        <div className="absolute right-5 top-5"><ThemeToggle /></div>
        <div className="w-full max-w-md">
          <div className="login-mobile-brand mb-10 lg:hidden">Evaly / พื้นที่การสอบ</div>
          {children}
        </div>
      </main>
    </div>
  );
}
