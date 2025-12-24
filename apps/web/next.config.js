/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  assetPrefix: 'https://8rbiz85j24tm.space.minimax.io',
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