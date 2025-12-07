/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config) {
    config.module.rules.push({
      test: /pdf\.worker\.mjs$/,
      type: "asset/resource",
    });
    return config;
  },
};

module.exports = nextConfig;
