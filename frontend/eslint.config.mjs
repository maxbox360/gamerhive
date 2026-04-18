import { defineConfig } from "eslint/config";
// Patch module resolution like eslint-config-next does so plugins (e.g. @next/eslint-plugin-next)
// resolve correctly when using the shareable configs by name.
import "@rushstack/eslint-patch/modern-module-resolution";

// Use the shareable configs by name to avoid importing internal files.
export default defineConfig({
  extends: ["next/core-web-vitals", "next/typescript"],
  ignorePatterns: [".next/**", "out/**", "build/**", "next-env.d.ts"],
});
