/**
 * Utility validation functions.
 *
 * These are pure functions for validating values without Vue composition API.
 */

/**
 * Check if a value is empty (null, undefined, empty string, empty array).
 * @param {any} value - Value to check
 * @returns {boolean}
 */
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

/**
 * Check if a value is a valid email.
 * @param {string} email - Email to validate
 * @returns {boolean}
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Check if a value is a valid URL.
 * @param {string} url - URL to validate
 * @returns {boolean}
 */
export const isValidUrl = (url) => {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Check if a value is a positive number.
 * @param {any} value - Value to check
 * @returns {boolean}
 */
export const isPositiveNumber = (value) => {
  const num = Number(value);
  return !isNaN(num) && num > 0;
};

/**
 * Check if a value is a non-negative number.
 * @param {any} value - Value to check
 * @returns {boolean}
 */
export const isNonNegativeNumber = (value) => {
  const num = Number(value);
  return !isNaN(num) && num >= 0;
};

/**
 * Check if a value is within a range.
 * @param {number} value - Value to check
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {boolean}
 */
export const isInRange = (value, min, max) => {
  const num = Number(value);
  return !isNaN(num) && num >= min && num <= max;
};

/**
 * Check if a date is valid.
 * @param {any} date - Date to validate
 * @returns {boolean}
 */
export const isValidDate = (date) => {
  if (!date) return false;
  const d = new Date(date);
  return !isNaN(d.getTime());
};

/**
 * Check if a date is in the future.
 * @param {any} date - Date to check
 * @returns {boolean}
 */
export const isFutureDate = (date) => {
  if (!isValidDate(date)) return false;
  return new Date(date) > new Date();
};

/**
 * Check if a date is in the past.
 * @param {any} date - Date to check
 * @returns {boolean}
 */
export const isPastDate = (date) => {
  if (!isValidDate(date)) return false;
  return new Date(date) < new Date();
};

/**
 * Check if start date is before end date.
 * @param {any} startDate - Start date
 * @param {any} endDate - End date
 * @returns {boolean}
 */
export const isValidDateRange = (startDate, endDate) => {
  if (!isValidDate(startDate) || !isValidDate(endDate)) return false;
  return new Date(startDate) <= new Date(endDate);
};

/**
 * Check if a string matches an identifier pattern (alphanumeric + dash/underscore).
 * @param {string} value - String to check
 * @returns {boolean}
 */
export const isValidIdentifier = (value) => {
  if (!value) return false;
  return /^[a-zA-Z0-9\-_]+$/.test(value);
};

/**
 * Check if a phone number is valid (basic check).
 * @param {string} phone - Phone number to check
 * @returns {boolean}
 */
export const isValidPhone = (phone) => {
  if (!phone) return false;
  return /^[\d\s\-\+\(\)]+$/.test(phone) && phone.replace(/\D/g, '').length >= 7;
};

/**
 * Check string length.
 * @param {string} value - String to check
 * @param {number} min - Minimum length
 * @param {number} max - Maximum length
 * @returns {boolean}
 */
export const isValidLength = (value, min = 0, max = Infinity) => {
  if (typeof value !== 'string') return false;
  return value.length >= min && value.length <= max;
};
