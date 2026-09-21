import fs from 'fs';
import path from 'path';

function patchFile(relPath, transform) {
  const fullPath = path.resolve(relPath);
  let content = fs.readFileSync(fullPath, 'utf8').replace(/\r\n/g, '\n');
  content = transform(content);
  fs.writeFileSync(fullPath, content, 'utf8');
  console.log(`Patched ${relPath} successfully.`);
}

// 1. Patch Navbar.tsx
patchFile('client/components/Navbar.tsx', c => {
  // Replace imports
  c = c.replace(
    /import \{[^}]*\} from "lucide-react";\nimport \{ Link, NavLink, useNavigate \} from "react-router-dom";\nimport \{ useAuth \} from "@\/contexts\/AuthContext";\nimport \{ ThemeToggle \} from "@\/components\/ThemeToggle";\nimport \{ NotificationBell \} from "@\/components\/NotificationBell";\nimport \{[\s\S]*?\} from "@\/components\/ui\/dropdown-menu";/,
    `import { BookOpen, History, Home, UserCircle } from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { NotificationBell } from "@/components/NotificationBell";
import { UserProfileMenu } from "@/components/UserProfileMenu";`
  );

  // Add Profile link in nav
  c = c.replace(
    /(<NavLink[\s\S]*?to="\/history"[\s\S]*?<\/NavLink>\s*\)\s*\}\s*<\/nav>)/,
    `$1`.replace('</nav>', `  <NavLink
            to="/profile"
            aria-label="โปรไฟล์"
            className={({ isActive }) => \`app-nav-link \${isActive ? "app-nav-link-active" : ""}\`}
          >
            <UserCircle size={16} /> <span>โปรไฟล์</span>
          </NavLink>
        </nav>`)
  );

  // If student history is not rendered, also support adding profile before </nav>
  if (!c.includes('to="/profile"')) {
    c = c.replace(
      '</nav>',
      `  <NavLink
            to="/profile"
            aria-label="โปรไฟล์"
            className={({ isActive }) => \`app-nav-link \${isActive ? "app-nav-link-active" : ""}\`}
          >
            <UserCircle size={16} /> <span>โปรไฟล์</span>
          </NavLink>
        </nav>`
    );
  }

  // Replace dropdown menu with UserProfileMenu
  c = c.replace(
    /<DropdownMenu>[\s\S]*?<\/DropdownMenu>/,
    `<UserProfileMenu />`
  );

  // Remove unused navigate / handleLogout if present
  c = c.replace(/const navigate = useNavigate\(\);\s*const handleLogout[\s\S]*?};\s*/, '');
  return c;
});

// 2. Patch RoomDetail.tsx
patchFile('client/pages/RoomDetail.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { NotificationBell } from "@/components/NotificationBell";',
      `import { NotificationBell } from "@/components/NotificationBell";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /<div className="flex items-center gap-1">\s*<ThemeToggle \/>\s*<NotificationBell \/>/,
    `<div className="flex items-center gap-2">\n          <ThemeToggle />\n          <NotificationBell />\n          <UserProfileMenu />`
  );

  return c;
});

// 3. Patch ExamSubmit.tsx
patchFile('client/pages/ExamSubmit.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { ThemeToggle } from "@/components/ThemeToggle";',
      `import { ThemeToggle } from "@/components/ThemeToggle";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /<ThemeToggle \/>\s*<\/div>\s*<\/header>/,
    `<ThemeToggle />\n          <UserProfileMenu />\n        </div>\n      </header>`
  );

  return c;
});

// 4. Patch StudentGrading.tsx
patchFile('client/pages/StudentGrading.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { ThemeToggle } from "@/components/ThemeToggle";',
      `import { ThemeToggle } from "@/components/ThemeToggle";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /<ThemeToggle \/>\s*<\/header>/,
    `<div className="flex items-center gap-2">\n          <ThemeToggle />\n          <UserProfileMenu />\n        </div>\n      </header>`
  );

  return c;
});

// 5. Patch CreateExam.tsx
patchFile('client/pages/CreateExam.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { ThemeToggle } from "@/components/ThemeToggle";',
      `import { ThemeToggle } from "@/components/ThemeToggle";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /(<span className="hidden sm:inline">\{isSaving \? "กำลังเผยแพร่…" : "เผยแพร่"\}<\/span>\s*<\/Button>\s*<\/div>)/,
    `$1\n          <ThemeToggle />\n          <UserProfileMenu />`
  );

  return c;
});

// 6. Patch EditExam.tsx
patchFile('client/pages/EditExam.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { ThemeToggle } from "@/components/ThemeToggle";',
      `import { ThemeToggle } from "@/components/ThemeToggle";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /(<Button onClick=\{handleSave\}[\s\S]*?<\/Button>\s*<\/div>)/,
    `$1`.replace('</div>', `  <UserProfileMenu />\n        </div>`)
  );

  return c;
});

// 7. Patch Chapter3LLMTest.tsx
patchFile('client/pages/Chapter3LLMTest.tsx', c => {
  if (!c.includes('UserProfileMenu')) {
    c = c.replace(
      'import { ThemeToggle } from "@/components/ThemeToggle";',
      `import { ThemeToggle } from "@/components/ThemeToggle";\nimport { UserProfileMenu } from "@/components/UserProfileMenu";`
    );
  }

  c = c.replace(
    /(<div className="flex items-center gap-3">\s*<ThemeToggle \/>\s*<\/div>)/,
    `<div className="flex items-center gap-3">\n          <ThemeToggle />\n          <UserProfileMenu />\n        </div>`
  );

  return c;
});

console.log('All navbars successfully updated with Profile!');
