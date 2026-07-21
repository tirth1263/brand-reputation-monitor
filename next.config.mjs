/** @type {import('next').NextConfig} */
const isGitHubPages = process.env.GITHUB_PAGES === "true";

const nextConfig = {
  poweredByHeader: false,
  ...(isGitHubPages
    ? {
        output: "export",
        basePath: "/brand-reputation-monitor",
        assetPrefix: "/brand-reputation-monitor/",
        trailingSlash: true,
      }
    : {}),
  experimental: {
    serverActions: { bodySizeLimit: "2mb" },
  },
};

export default nextConfig;
