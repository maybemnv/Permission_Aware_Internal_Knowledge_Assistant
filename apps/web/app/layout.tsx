import type { Metadata } from "next";
import "./tokens.css";

export const metadata: Metadata = {
  title: "Evidence Desk | Permission-aware knowledge",
  description: "A permission-safe internal knowledge workbench.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell" aria-label="Permission-aware internal knowledge assistant">
          {children}
          <footer className="site-footer">
            <span>Fixture-backed prototype</span>
            <span>Permission checks remain server-side at integration time.</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
