/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/3D_SFM',
  images: {
    unoptimized: true,
  },
  // Disable server-side features for static export
  trailingSlash: true,
};

export default nextConfig;
