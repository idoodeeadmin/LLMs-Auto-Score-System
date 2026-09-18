import { Skeleton } from "@/components/ui/skeleton";
import { RoomStreamSkeleton } from "@/components/PageSkeletons";

export type LoadingLayout = "form" | "table" | "analytics" | "document" | "auth";

export function ContentSkeleton({ layout = "document" }: { layout?: LoadingLayout }) {
  return <div role="status" aria-busy="true" className="space-y-6">
    <span className="sr-only">กำลังโหลดข้อมูล</span>
    <div aria-hidden="true" className="space-y-6">
      <Skeleton className="h-7 w-1/2 max-w-72" />
      <Skeleton className="h-4 w-2/3" />
      {layout === "analytics" && <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {[0, 1, 2].map(i => <Skeleton key={i} className="h-24" />)}
      </div>}
      {layout === "table" ? <div className="divide-y rounded-lg border bg-card px-4">
        {Array.from({ length: 6 }, (_, i) => <div key={i} className="flex gap-4 py-5">
          <Skeleton className="h-5 w-1/2" /><Skeleton className="ml-auto h-5 w-1/4" />
        </div>)}
      </div> : layout === "form" || layout === "auth" ? <div className="space-y-5 rounded-lg border bg-card p-6">
        {[0, 1, 2].map(i => <div className="space-y-2" key={i}>
          <Skeleton className="h-4 w-24" /><Skeleton className="h-11 w-full" />
        </div>)}
        <Skeleton className="h-10 w-28" />
      </div> : <div className="space-y-4">
        {[0, 1, 2].map(i => <div key={i} className="space-y-4 rounded-lg border bg-card p-6">
          <Skeleton className="h-5 w-3/4" /><Skeleton className="h-4 w-full" />
          <Skeleton className={layout === "analytics" ? "h-40 w-full" : "h-4 w-2/3"} />
        </div>)}
      </div>}
    </div>
  </div>;
}

export function PageLoading({ layout = "document" }: { layout?: LoadingLayout }) {
  return <div className="min-h-screen bg-background">
    {layout !== "auth" && <div aria-hidden="true" className="flex h-16 items-center justify-between border-b px-6">
      <Skeleton className="h-8 w-32" /><Skeleton className="h-8 w-20" />
    </div>}
    <main className={layout === "auth" ? "mx-auto max-w-lg px-4 py-16" : "mx-auto max-w-5xl px-4 py-8"}>
      <ContentSkeleton layout={layout} />
    </main>
  </div>;
}

export function RouteLoading({ pathname }: { pathname: string }) {
  if (/^\/room\/[^/]+\/?$/.test(pathname)) return <RoomStreamSkeleton />;
  if (["/", "/register", "/forgot-password", "/reset-password", "/verify-email", "/select-role"].includes(pathname))
    return <PageLoading layout="auth" />;
  if (/analytics$/.test(pathname)) return <PageLoading layout="analytics" />;
  if (/(review|scoreboard|history|stats|home)$/.test(pathname)) return <PageLoading layout="table" />;
  if (/(create-exam|edit|profile)$/.test(pathname)) return <PageLoading layout="form" />;
  return <PageLoading />;
}
