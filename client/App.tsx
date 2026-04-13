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
import ExamView from "./pages/ExamView";
import RoomReview from "./pages/RoomReview";
import StudentGrading from "./pages/StudentGrading";
import ExamSubmit from "./pages/ExamSubmit";

const queryClient = new QueryClient();

import { AuthProvider } from "./contexts/AuthContext";

export const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/room/:roomId/create-exam" element={<CreateExam />} />
            <Route path="/" element={<Index />} />
            <Route path="/register" element={<Register />} />
            <Route path="/home" element={<Home />} />
            <Route path="/room/:roomId/exam/:examId/submit" element={<ExamSubmit />} />
            <Route path="/room/:roomId/exam/:examId" element={<ExamView />} />
            <Route path="/room/:roomId/exam/:examId/grading/:studentId" element={<StudentGrading />} />
            <Route path="/room/:roomId" element={<RoomDetail />} />
            <Route path="/room/:roomId/exam/:examId/review" element={<RoomReview />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);
