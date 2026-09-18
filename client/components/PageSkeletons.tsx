import { Skeleton } from "@/components/ui/skeleton";

const tone = "bg-slate-200/80 dark:bg-slate-800";
const card = "rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900";

function LoadingLabel({ label }: { label: string }) {
  return <span className="sr-only">{label}</span>;
}

function HeaderSkeleton() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900 md:px-8">
      <div className="flex items-center gap-3">
        <Skeleton className={`${tone} h-9 w-9 rounded-full`} />
        <div className="space-y-2">
          <Skeleton className={`${tone} h-4 w-32`} />
          <Skeleton className={`${tone} h-3 w-20`} />
        </div>
      </div>
      <div className="flex gap-2">
        <Skeleton className={`${tone} h-9 w-9 rounded-full`} />
        <Skeleton className={`${tone} h-9 w-9 rounded-full`} />
      </div>
    </header>
  );
}

function FeedCardSkeleton() {
  return (
    <div className={`${card} p-5`}>
      <div className="flex gap-3">
        <Skeleton className={`${tone} h-10 w-10 shrink-0 rounded-full`} />
        <div className="w-full space-y-3">
          <div className="flex items-start justify-between gap-6">
            <div className="space-y-2">
              <Skeleton className={`${tone} h-4 w-44 max-w-full`} />
              <Skeleton className={`${tone} h-3 w-24`} />
            </div>
            <Skeleton className={`${tone} h-8 w-8 rounded-full`} />
          </div>
          <Skeleton className={`${tone} h-4 w-4/5`} />
          <Skeleton className={`${tone} h-4 w-3/5`} />
          <div className="flex gap-2 pt-2">
            <Skeleton className={`${tone} h-9 w-24`} />
            <Skeleton className={`${tone} h-9 w-28`} />
          </div>
        </div>
      </div>
    </div>
  );
}

export function RoomStreamSkeleton() {
  return (
    <div role="status" aria-busy="true" className="min-h-screen bg-[#f8f9fa] dark:bg-slate-950">
      <LoadingLabel label="กำลังโหลดห้องเรียน" />
      <HeaderSkeleton />
      <main className="mx-auto max-w-6xl px-3 pb-12 pt-5 sm:px-5">
        <Skeleton className={`${tone} mb-6 h-40 w-full rounded-xl`} />
        <div className="grid gap-5 lg:grid-cols-[230px_minmax(0,1fr)]">
          <aside className="space-y-4">
            <div className={`${card} space-y-3 p-5`}>
              <Skeleton className={`${tone} h-3 w-24`} />
              <Skeleton className={`${tone} h-7 w-28`} />
              <Skeleton className={`${tone} h-3 w-20`} />
            </div>
            <div className={`${card} space-y-3 p-5`}>
              <Skeleton className={`${tone} h-4 w-20`} />
              <Skeleton className={`${tone} h-3 w-full`} />
              <Skeleton className={`${tone} h-3 w-4/5`} />
            </div>
          </aside>
          <section className="space-y-4">
            <div className={`${card} flex items-center gap-3 p-4`}>
              <Skeleton className={`${tone} h-10 w-10 rounded-full`} />
              <Skeleton className={`${tone} h-10 flex-1 rounded-full`} />
            </div>
            <FeedCardSkeleton />
            <FeedCardSkeleton />
            <FeedCardSkeleton />
          </section>
        </div>
      </main>
    </div>
  );
}

export function ExamPageSkeleton({ singleColumn = false }: { singleColumn?: boolean }) {
  return (
    <div role="status" aria-busy="true" className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <LoadingLabel label="กำลังโหลดข้อสอบ" />
      <HeaderSkeleton />
      <main className={`mx-auto ${singleColumn ? "max-w-4xl" : "max-w-6xl"} px-4 py-8`}>
        <Skeleton className={`${tone} mb-6 h-5 w-28`} />
        <div className={singleColumn ? "space-y-6" : "grid items-start gap-6 lg:grid-cols-3"}>
          <section className="space-y-6 lg:col-span-2">
            <div className={`${card} space-y-5 p-6 sm:p-8`}>
              <Skeleton className={`${tone} h-7 w-3/4`} />
              <Skeleton className={`${tone} h-4 w-1/2`} />
              <div className="flex gap-8 border-t border-slate-100 pt-5 dark:border-slate-800">
                <Skeleton className={`${tone} h-10 w-24`} />
                <Skeleton className={`${tone} h-10 w-24`} />
                <Skeleton className={`${tone} h-10 w-20`} />
              </div>
            </div>
            <Skeleton className={`${tone} h-4 w-32`} />
            <FeedCardSkeleton />
            <FeedCardSkeleton />
          </section>
          {!singleColumn && <aside className={`${card} p-6`}>
            <Skeleton className={`${tone} h-11 w-full`} />
            <Skeleton className={`${tone} mt-4 h-4 w-3/4`} />
            <Skeleton className={`${tone} mt-2 h-4 w-1/2`} />
          </aside>}
        </div>
      </main>
    </div>
  );
}

export function WorkspaceRouteSkeleton() {
  return (
    <div role="status" aria-busy="true" className="min-h-screen bg-slate-50 dark:bg-slate-950">
      <LoadingLabel label="กำลังโหลดหน้า" />
      <HeaderSkeleton />
      <main className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        <div className="space-y-3">
          <Skeleton className={`${tone} h-7 w-2/3 max-w-56`} />
          <Skeleton className={`${tone} h-4 w-80 max-w-full`} />
        </div>
        <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_240px]">
          <section className="space-y-4">
            <FeedCardSkeleton />
            <FeedCardSkeleton />
            <FeedCardSkeleton />
          </section>
          <aside className={`${card} hidden space-y-3 p-5 md:block`}>
            <Skeleton className={`${tone} h-4 w-24`} />
            <Skeleton className={`${tone} h-3 w-full`} />
            <Skeleton className={`${tone} h-3 w-4/5`} />
            <Skeleton className={`${tone} h-9 w-full`} />
          </aside>
        </div>
      </main>
    </div>
  );
}

export function RoomListSkeleton() {
  return (
    <div role="status" aria-busy="true" className="room-card-grid">
      <LoadingLabel label="กำลังโหลดห้องเรียน" />
      {[0, 1, 2].map((item) => (
        <div className="overflow-hidden rounded-xl border bg-white dark:bg-slate-900" key={item}>
          <div className="h-[126px] bg-slate-300 p-5 dark:bg-slate-800">
            <Skeleton className="h-5 w-48 max-w-full bg-white/30" />
            <Skeleton className="mt-3 h-3 w-24 bg-white/25" />
            <Skeleton className="mt-2 h-3 w-32 bg-white/20" />
          </div>
          <div className="space-y-3 p-5">
            <Skeleton className={`${tone} h-3 w-20`} />
            <Skeleton className={`${tone} h-4 w-28`} />
            <Skeleton className={`${tone} h-3 w-44 max-w-full`} />
          </div>
          <div className="border-t p-3"><Skeleton className={`${tone} h-8 w-28`} /></div>
        </div>
      ))}
    </div>
  );
}
