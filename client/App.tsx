import "./global.css";
import "./workspace.css";

import { lazy, Suspense, useEffect } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider, Routes, Route, useLocation } from "react-router-dom";
const Index = lazy(() => import("./pages/Index"));
const Register = lazy(() => import("./pages/Register"));
const ForgotPassword = lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = lazy(() => import("./pages/ResetPassword"));
const SelectRole = lazy(() => import("./pages/SelectRole"));
const NotFound = lazy(() => import("./pages/NotFound"));

const Home = lazy(() => import("./pages/Home"));
const RoomDetail = lazy(() => import("./pages/RoomDetail"));
const CreateExam = lazy(() => import("./pages/CreateExam"));
const ExamSubmit = lazy(() => import("./pages/ExamSubmit"));
const StudentGrading = lazy(() => import("./pages/StudentGrading"));
const ExamView = lazy(() => import("./pages/ExamView"));
const EditExam = lazy(() => import("./pages/EditExam"));
const RoomReview = lazy(() => import("./pages/RoomReview"));
const ExamScoreboard = lazy(() => import("./pages/ExamScoreboard"));
const RoomAnalytics = lazy(() => import("./pages/RoomAnalytics"));
const TeacherAnalytics = lazy(() => import("./pages/TeacherAnalytics"));
const StudentHistory = lazy(() => import("./pages/StudentHistory"));
const Profile = lazy(() => import("./pages/Profile"));
const AnnouncementStats = lazy(() => import("./pages/AnnouncementStats"));
const VerifyEmail = lazy(() => import("./pages/VerifyEmail"));
const Chapter3LLMTest = lazy(() => import("./pages/Chapter3LLMTest"));
const Chapter3Demo = lazy(() => import("./pages/Chapter3Demo"));
const Chapter3App = lazy(() => import("./pages/Chapter3App"));

const queryClient = new QueryClient();

import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { RouteLoading } from "./components/RouteLoading";

function RouteExperience() {
  const location = useLocation();
  const { isLoading } = useAuth();
  const isLabRoute = ["/chapter3-llm-test", "/test-llm", "/chapter3-demo", "/chapter3-app"].some(
    (route) => location.pathname.startsWith(route),
  );

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "auto" });
  }, [location.pathname]);

  return (
    <div className={`evaly-app ${isLabRoute ? "evaly-lab" : "evaly-product"}`}>
      {isLoading ? <RouteLoading pathname={location.pathname} /> : <Suspense fallback={<RouteLoading pathname={location.pathname} />}>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/select-role" element={<SelectRole />} />
          <Route path="/home" element={<Home />} />
          <Route path="/room/:roomId" element={<RoomDetail />} />
          <Route path="/room/:roomId/create-exam" element={<CreateExam />} />
          <Route path="/room/:roomId/analytics" element={<RoomAnalytics />} />
          <Route path="/room/:roomId/announcement/:annId/stats" element={<AnnouncementStats />} />
          <Route path="/room/:roomId/exam/:examId" element={<ExamView />} />
          <Route path="/room/:roomId/exam/:examId/edit" element={<EditExam />} />
          <Route path="/room/:roomId/exam/:examId/review" element={<RoomReview />} />
          <Route path="/room/:roomId/exam/:examId/scoreboard" element={<ExamScoreboard />} />
          <Route path="/room/:roomId/exam/:examId/analytics" element={<TeacherAnalytics />} />
          <Route path="/room/:roomId/exam/:examId/submit" element={<ExamSubmit />} />
          <Route path="/room/:roomId/exam/:examId/grading/:studentId" element={<StudentGrading />} />
          <Route path="/history" element={<StudentHistory />} />
          <Route path="/profile" element={<Profile />} />
          {import.meta.env.DEV && (
            <>
              <Route path="/chapter3-llm-test" element={<Chapter3LLMTest />} />
              <Route path="/test-llm" element={<Chapter3LLMTest />} />
              <Route path="/chapter3-demo" element={<Chapter3Demo />} />
              <Route path="/chapter3-app" element={<Chapter3App />} />
            </>
          )}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>}
    </div>
  );
}

const router = createBrowserRouter([{ path: "*", element: <RouteExperience /> }]);

export const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="system" storageKey="evaly-theme">
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <RouterProvider router={router} />
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);
