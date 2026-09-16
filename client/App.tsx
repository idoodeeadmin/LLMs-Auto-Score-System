import "./global.css";
import "./workspace.css";

import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Register from "./pages/Register";
import Home from "./pages/Home";
import SelectRole from "./pages/SelectRole";
import RoomDetail from "./pages/RoomDetail";
import CreateExam from "./pages/CreateExam";
import ExamSubmit from "./pages/ExamSubmit";
import StudentGrading from "./pages/StudentGrading";
import Chapter3LLMTest from "./pages/Chapter3LLMTest";
import Chapter3Demo from "./pages/Chapter3Demo";
import Chapter3App from "./pages/Chapter3App";
import NotFound from "./pages/NotFound";

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
              <Route path="/" element={<Index />} />
              <Route path="/register" element={<Register />} />
              <Route path="/select-role" element={<SelectRole />} />
              <Route path="/home" element={<Home />} />
              <Route path="/room/:roomId" element={<RoomDetail />} />
              <Route path="/room/:roomId/create-exam" element={<CreateExam />} />
              <Route path="/room/:roomId/exam/:examId/submit" element={<ExamSubmit />} />
              <Route path="/room/:roomId/exam/:examId/grading/:studentId" element={<StudentGrading />} />
              <Route path="/chapter3-llm-test" element={<Chapter3LLMTest />} />
              <Route path="/test-llm" element={<Chapter3LLMTest />} />
              <Route path="/chapter3-demo" element={<Chapter3Demo />} />
              <Route path="/chapter3-app" element={<Chapter3App />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);
