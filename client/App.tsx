import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Register from "./pages/Register";
import Home from "./pages/Home";
import RoomDetail from "./pages/RoomDetail";
import NotFound from "./pages/NotFound";
import CreateExam from "./pages/CreateExam";
import EditExam from "./pages/EditExam";
import ExamView from "./pages/ExamView";
import RoomReview from "./pages/RoomReview";
import StudentGrading from "./pages/StudentGrading";
import ExamSubmit from "./pages/ExamSubmit";
import TeacherAnalytics from "./pages/TeacherAnalytics";
import RoomAnalytics from "./pages/RoomAnalytics";
import ExamScoreboard from "./pages/ExamScoreboard";
import StudentHistory from "./pages/StudentHistory";
import Profile from "./pages/Profile";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import VerifyEmail from "./pages/VerifyEmail";

const queryClient = new QueryClient();

import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";

export const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="system" storageKey="evaly-theme">
      <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/room/:roomId/create-exam" element={<CreateExam />} />
            <Route path="/room/:roomId/exam/:examId/edit" element={<EditExam />} />
            <Route path="/" element={<Index />} />
            <Route path="/register" element={<Register />} />
            <Route path="/home" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/history" element={<StudentHistory />} />
            <Route path="/room/:roomId/analytics" element={<RoomAnalytics />} />
            <Route path="/room/:roomId/exam/:examId/scoreboard" element={<ExamScoreboard />} />
            <Route path="/room/:roomId/exam/:examId/submit" element={<ExamSubmit />} />
            <Route path="/room/:roomId/exam/:examId" element={<ExamView />} />
            <Route path="/room/:roomId/exam/:examId/analytics" element={<TeacherAnalytics />} />
            <Route path="/room/:roomId/exam/:examId/grading/:studentId" element={<StudentGrading />} />
            <Route path="/room/:roomId" element={<RoomDetail />} />
            <Route path="/room/:roomId/exam/:examId/review" element={<RoomReview />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);
