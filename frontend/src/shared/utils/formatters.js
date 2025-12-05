/**
 * Utility functions for formatting values.
 *
 * These are pure functions that can be used anywhere without Vue composition API.
 */

/**
 * Format a number with thousand separators.
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
export const formatNumber = (value, decimals = 0) => {
  if (value === null || value === undefined) return '-';
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Format a percentage.
 * @param {number} value - Percentage value (0-100)
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value, decimals = 0) => {
  if (value === null || value === undefined) return '-';
  return `${formatNumber(value, decimals)}%`;
};

/**
 * Format currency.
 * @param {number} value - Currency value
 * @param {string} currency - Currency code
 * @returns {string} Formatted currency
 */
export const formatCurrency = (value, currency = 'USD') => {
  if (value === null || value === undefined) return '-';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(value);
};

/**
 * Format bytes to human readable size.
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
export const formatBytes = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * Truncate text with ellipsis.
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

/**
 * Convert snake_case to Title Case.
 * @param {string} str - String in snake_case
 * @returns {string} Title Case string
 */
export const snakeToTitle = (str) => {
  if (!str) return '';
  return str
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Convert camelCase to Title Case.
 * @param {string} str - String in camelCase
 * @returns {string} Title Case string
 */
export const camelToTitle = (str) => {
  if (!str) return '';
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
};

/**
 * Calculate progress percentage.
 * @param {number} current - Current value
 * @param {number} total - Total value
 * @returns {number} Percentage (0-100)
 */
export const calculateProgress = (current, total) => {
  if (!total || total === 0) return 0;
  return Math.min(Math.round((current / total) * 100), 100);
};

/**
 * Get progress status for Element Plus progress component.
 * @param {number} percentage - Progress percentage
 * @returns {string} Status ('success', 'warning', 'exception', '')
 */
export const getProgressStatus = (percentage) => {
  if (percentage >= 100) return 'success';
  if (percentage >= 75) return '';
  if (percentage >= 50) return 'warning';
  return 'exception';
};

/**
 * Format quantity with unit.
 * @param {number} value - Quantity value
 * @param {string} unit - Unit string
 * @returns {string} Formatted quantity
 */
export const formatQuantity = (value, unit = 'pcs') => {
  if (value === null || value === undefined) return '-';
  return `${formatNumber(value)} ${unit}`;
};

/**
 * Generate initials from a name.
 * @param {string} name - Full name
 * @returns {string} Initials (e.g., "John Doe" -> "JD")
 */
export const getInitials = (name) => {
  if (!name) return '';
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};
