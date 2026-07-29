"use client";

import Link from "next/link";
import { EuiPanel, EuiTitle, EuiText, EuiButton, EuiSpacer } from "@elastic/eui";

export default function NotFound() {
  const msg = "404 — The map doesn't lead anywhere.";

  return (
    <div style={{ minHeight: "70vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <EuiPanel paddingSize="l" style={{ maxWidth: 720, backgroundColor: "#161616" }}>
        <EuiTitle size="m">
          <h1 style={{ color: "#FFD700" }}>404 — Page not found</h1>
        </EuiTitle>
        <EuiSpacer />
        <EuiText color="subdued">
          <p style={{ fontSize: 18 }}>{msg}</p>
        </EuiText>
        <EuiSpacer />
        <div style={{ display: "flex", gap: 8 }}>
          <Link href="/games">
            <EuiButton color="primary">Browse games</EuiButton>
          </Link>
          <Link href="/">
            <EuiButton>Home</EuiButton>
          </Link>
        </div>
      </EuiPanel>
    </div>
  );
}
