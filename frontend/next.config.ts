/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbopack: {
      // This tells Next.js to stay inside the project folder
      root: '.', 
    },
  },
};

export default nextConfig;