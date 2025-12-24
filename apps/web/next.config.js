/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/video-renderer/:path*',
        destination: 'http://localhost:8001/:path*',
      },
      {
        source: '/api/animation-engine/:path*',
        destination: 'http://localhost:8002/:path*',
      },
    ];
  },
};

module.exports = nextConfig;