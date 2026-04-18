"use client";

import { EuiProvider } from "@elastic/eui";
import { ReactNode } from "react";
import createCache from "@emotion/cache";

// Create Emotion cache for EUI
const cache = createCache({
  key: "eui",
  container: typeof document !== "undefined" ? document.head : undefined,
});
cache.compat = true;

interface ProvidersProps {
  children: ReactNode;
}

export default function Providers({ children }: ProvidersProps) {
  return (
    <EuiProvider colorMode="dark" cache={cache}>
      {children}
    </EuiProvider>
  );
}

