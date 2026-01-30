/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  // No basePath needed for custom domain
  images: {
    unoptimized: true,
  },
  // Disable server-side features for static export
  trailingSlash: true,
};

export default nextConfig;
