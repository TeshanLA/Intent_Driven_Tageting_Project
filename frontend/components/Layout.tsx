import Link from "next/link";
import type { ReactNode } from "react";

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="page-shell">
      <header className="site-header">
        <div>
          <Link className="brand-mark" href="/">
            PulsePress
          </Link>
          <p className="brand-copy">Demo publisher for privacy-preserving ad targeting</p>
        </div>
        <nav className="nav-links">
          <Link href="/">Articles</Link>
          <Link href="/dashboard">Dashboard</Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
