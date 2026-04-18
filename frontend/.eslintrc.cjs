// CommonJS ESLint config to ensure @rushstack/eslint-patch runs correctly
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  extends: ['next/core-web-vitals', 'next/typescript'],
  ignorePatterns: ['.next/**', 'out/**', 'build/**', 'next-env.d.ts'],
};

