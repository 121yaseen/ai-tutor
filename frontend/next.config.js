/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/events/:path*',
        destination: 'http://localhost:8000/events/:path*',
      },
    ]
  },
}

module.exports = nextConfig 