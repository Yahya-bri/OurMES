/**
 * DateTime composable for consistent date/time formatting across the application.
 *
 * Usage:
 *   import { useDateTime } from '@/shared/composables/useDateTime';
 *   const { formatDate, formatDateTime, formatTime, getRelativeTime } = useDateTime();
 */
import { computed } from 'vue';

export function useDateTime(options = {}) {
  const locale = options.locale || 'en-US';

  /**
   * Format a date string to a readable date format.
   * @param {string|Date} dateStr - The date to format
   * @param {string} format - 'short', 'medium', 'long'
   * @returns {string} Formatted date string
   */
  const formatDate = (dateStr, format = 'medium') => {
    if (!dateStr) return '-';

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '-';

      const formats = {
        short: { month: 'numeric', day: 'numeric', year: '2-digit' },
        medium: { month: 'short', day: 'numeric', year: 'numeric' },
        long: { month: 'long', day: 'numeric', year: 'numeric', weekday: 'short' },
      };

      return date.toLocaleDateString(locale, formats[format] || formats.medium);
    } catch {
      return '-';
    }
  };

  /**
   * Format a date string to include time.
   * @param {string|Date} dateStr - The date to format
   * @returns {string} Formatted date and time string
   */
  const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '-';

      return date.toLocaleString(locale, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '-';
    }
  };

  /**
   * Format time only.
   * @param {string|Date} dateStr - The date to extract time from
   * @returns {string} Formatted time string
   */
  const formatTime = (dateStr) => {
    if (!dateStr) return '-';

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '-';

      return date.toLocaleTimeString(locale, {
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '-';
    }
  };

  /**
   * Get relative time (e.g., "2 hours ago", "in 3 days").
   * @param {string|Date} dateStr - The date to compare
   * @returns {string} Relative time string
   */
  const getRelativeTime = (dateStr) => {
    if (!dateStr) return '-';

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '-';

      const now = new Date();
      const diffMs = date - now;
      const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));
      const diffHours = Math.round(diffMs / (1000 * 60 * 60));
      const diffMins = Math.round(diffMs / (1000 * 60));

      if (Math.abs(diffDays) > 1) {
        return diffDays > 0 ? `in ${diffDays} days` : `${Math.abs(diffDays)} days ago`;
      }
      if (Math.abs(diffHours) >= 1) {
        return diffHours > 0 ? `in ${diffHours} hours` : `${Math.abs(diffHours)} hours ago`;
      }
      if (Math.abs(diffMins) >= 1) {
        return diffMins > 0 ? `in ${diffMins} minutes` : `${Math.abs(diffMins)} minutes ago`;
      }
      return 'just now';
    } catch {
      return '-';
    }
  };

  /**
   * Get deadline status and class.
   * @param {string|Date} deadline - The deadline date
   * @returns {object} { class: string, status: string, daysRemaining: number }
   */
  const getDeadlineStatus = (deadline) => {
    if (!deadline) return { class: '', status: 'none', daysRemaining: null };

    const now = new Date();
    const deadlineDate = new Date(deadline);
    const daysUntil = (deadlineDate - now) / (1000 * 60 * 60 * 24);

    if (daysUntil < 0) {
      return { class: 'deadline overdue', status: 'overdue', daysRemaining: Math.floor(daysUntil) };
    }
    if (daysUntil < 2) {
      return { class: 'deadline urgent', status: 'urgent', daysRemaining: Math.ceil(daysUntil) };
    }
    if (daysUntil < 7) {
      return { class: 'deadline warning', status: 'warning', daysRemaining: Math.ceil(daysUntil) };
    }
    return { class: 'deadline normal', status: 'normal', daysRemaining: Math.ceil(daysUntil) };
  };

  /**
   * Format duration in seconds to human readable.
   * @param {number} seconds - Duration in seconds
   * @returns {string} Formatted duration
   */
  const formatDuration = (seconds) => {
    if (!seconds && seconds !== 0) return '-';

    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  /**
   * Parse ISO date string to Date object.
   * @param {string} dateStr - ISO date string
   * @returns {Date|null}
   */
  const parseDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? null : date;
  };

  return {
    formatDate,
    formatDateTime,
    formatTime,
    getRelativeTime,
    getDeadlineStatus,
    formatDuration,
    parseDate,
  };
}

export default useDateTime;
