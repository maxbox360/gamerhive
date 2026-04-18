import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@elastic/eui", "@elastic/datemath"],
};

export default nextConfig;
