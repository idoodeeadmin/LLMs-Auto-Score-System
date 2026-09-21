import fs from 'fs';
import path from 'path';

const file = path.resolve('client/pages/RoomReview.tsx');
let content = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');

// 1. Restore export default function RoomReview() and state
const target1 = `interface ExamInfo {
  id: number;
  title: string;
  total_score: number;
}
  const [isExportingXlsx, setIsExportingXlsx] = useState(false);`;

const replacement1 = `interface ExamInfo {
  id: number;
  title: string;
  total_score: number;
}

export default function RoomReview() {
  const navigate = useNavigate();
  const { roomId, examId } = useParams();
  const { user, token, isLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<"missing" | "pending" | "approved">("pending");
  const [subFilter, setSubFilter] = useState<"all" | "ready" | "needs_review">("all");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<"name" | "code" | "score_desc" | "score_asc">("name");
  const [students, setStudents] = useState<StudentSubmission[]>([]);
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [isFetching, setIsFetching] = useState(true);
  const [isApproving, setIsApproving] = useState(false);
  const [isExportingCsv, setIsExportingCsv] = useState(false);
  const [isExportingXlsx, setIsExportingXlsx] = useState(false);`;

if (!content.includes(target1)) {
  console.error("Target 1 not found!");
  process.exit(1);
}
content = content.replace(target1, replacement1);

// 2. Sort filteredStudents using useMemo
const target2 = `  const pageCount = Math.max(1, Math.ceil(filteredStudents.length / 20));
  const currentPage = Math.min(page, pageCount);
  const visibleStudents = filteredStudents.slice((currentPage - 1) * 20, currentPage * 20);`;

const replacement2 = `  const sortedStudents = useMemo(() => {
    return [...filteredStudents].sort((a, b) => {
      if (sortBy === "code") {
        return (a.student_code || "").localeCompare(b.student_code || "");
      }
      if (sortBy === "score_desc") {
        return (b.total_score ?? -1) - (a.total_score ?? -1);
      }
      if (sortBy === "score_asc") {
        return (a.total_score ?? -1) - (b.total_score ?? -1);
      }
      return a.name.localeCompare(b.name, "th");
    });
  }, [filteredStudents, sortBy]);

  const pageCount = Math.max(1, Math.ceil(sortedStudents.length / 20));
  const currentPage = Math.min(page, pageCount);
  const visibleStudents = sortedStudents.slice((currentPage - 1) * 20, currentPage * 20);`;

if (!content.includes(target2)) {
  console.error("Target 2 not found!");
  process.exit(1);
}
content = content.replace(target2, replacement2);

// 3. Add Sort Select dropdown next to search
const target3 = `            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                aria-label="ค้นหานักศึกษา"
                placeholder="ค้นหาชื่อ หรือ รหัส..."
                className="w-full pl-9 pr-4 h-10 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-gray-900 dark:text-white placeholder:text-gray-400"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>`;

const replacement3 = `            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                aria-label="ค้นหานักศึกษา"
                placeholder="ค้นหาชื่อ หรือ รหัส..."
                className="w-full pl-9 pr-4 h-10 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-gray-900 dark:text-white placeholder:text-gray-400"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="h-10 px-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-xs text-gray-700 dark:text-gray-300 focus:outline-none"
              aria-label="เรียงลำดับนักศึกษา"
            >
              <option value="name">เรียงตามชื่อ (ก-ฮ)</option>
              <option value="code">เรียงตามรหัสนิสิต</option>
              <option value="score_desc">คะแนน สูง → ต่ำ</option>
              <option value="score_asc">คะแนน ต่ำ → สูง</option>
            </select>`;

if (!content.includes(target3)) {
  console.error("Target 3 not found!");
  process.exit(1);
}
content = content.replace(target3, replacement3);

// 4. Clickable student name cell
const target4 = `                    <div className="review-name col-span-11 md:col-span-5 flex items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center font-medium text-sm text-blue-600 dark:text-blue-400 shrink-0">
                        {student.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-foreground">{student.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{student.student_code || student.email}</p>
                      </div>
                    </div>`;

const replacement4 = `                    <div
                      onClick={() => {
                        if (student.status !== "missing" && student.status !== "submitted" && student.status !== "grading") {
                          navigate(\`/room/\${roomId}/exam/\${examId}/grading/\${student.student_id}\`);
                        }
                      }}
                      className="review-name col-span-11 md:col-span-5 flex items-center gap-3 min-w-0 cursor-pointer group"
                      title={student.status !== "missing" ? "คลิกเพื่อตรวจทานคำตอบ" : undefined}
                    >
                      <div className="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center font-medium text-sm text-blue-600 dark:text-blue-400 shrink-0 group-hover:scale-105 transition-transform">
                        {student.name.charAt(0)}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-foreground group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                          {student.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{student.student_code || student.email}</p>
                      </div>
                    </div>`;

if (!content.includes(target4)) {
  console.error("Target 4 not found!");
  process.exit(1);
}
content = content.replace(target4, replacement4);

fs.writeFileSync(file, content, 'utf8');
console.log("Successfully patched RoomReview.tsx!");
