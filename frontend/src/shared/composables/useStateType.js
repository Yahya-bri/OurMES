/**
 * State type composable for consistent state display across the application.
 *
 * Provides functions to format state strings and get appropriate Element Plus tag types.
 *
 * Usage:
 *   import { useStateType } from '@/shared/composables/useStateType';
 *   const { getStateType, formatState, getStateColor } = useStateType();
 */

// State type mappings for Element Plus el-tag component
const ORDER_STATE_TYPES = {
  pending: 'warning',
  accepted: 'info',
  in_progress: '',
  completed: 'success',
  declined: 'danger',
  interrupted: 'warning',
  abandoned: 'info',
};

const TECHNOLOGY_STATE_TYPES = {
  draft: 'info',
  accepted: '',
  checked: 'success',
  outdated: 'warning',
  declined: 'danger',
};

const NCR_STATE_TYPES = {
  quarantine: 'danger',
  review: 'warning',
  closed: 'success',
};

const KANBAN_STATE_TYPES = {
  full: 'success',
  replenishing: 'warning',
  empty: 'danger',
};

const PRODUCTION_STATE_TYPES = {
  in_progress: '',
  completed: 'success',
};

const MAINTENANCE_TYPE_COLORS = {
  preventive: 'success',
  corrective: 'warning',
  breakdown: 'danger',
};

export function useStateType(context = 'order') {
  /**
   * Get state type mappings based on context.
   */
  const getStateMap = () => {
    const maps = {
      order: ORDER_STATE_TYPES,
      technology: TECHNOLOGY_STATE_TYPES,
      routing: TECHNOLOGY_STATE_TYPES,
      ncr: NCR_STATE_TYPES,
      kanban: KANBAN_STATE_TYPES,
      production: PRODUCTION_STATE_TYPES,
      maintenance: MAINTENANCE_TYPE_COLORS,
    };
    return maps[context] || ORDER_STATE_TYPES;
  };

  /**
   * Get Element Plus tag type for a state.
   * @param {string} state - The state value
   * @returns {string} Element Plus tag type ('', 'success', 'warning', 'danger', 'info')
   */
  const getStateType = (state) => {
    if (!state) return '';
    const stateMap = getStateMap();
    return stateMap[state] || '';
  };

  /**
   * Format state string to human-readable format.
   * Converts snake_case to Title Case.
   * @param {string} state - The state value
   * @returns {string} Formatted state string
   */
  const formatState = (state) => {
    if (!state) return '-';
    return state
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  /**
   * Get CSS color for a state.
   * @param {string} state - The state value
   * @returns {string} CSS color value
   */
  const getStateColor = (state) => {
    const colors = {
      // Success states
      success: '#67c23a',
      completed: '#67c23a',
      checked: '#67c23a',
      full: '#67c23a',
      // Warning states
      warning: '#e6a23c',
      pending: '#e6a23c',
      interrupted: '#e6a23c',
      replenishing: '#e6a23c',
      review: '#e6a23c',
      corrective: '#e6a23c',
      // Danger states
      danger: '#f56c6c',
      declined: '#f56c6c',
      quarantine: '#f56c6c',
      empty: '#f56c6c',
      breakdown: '#f56c6c',
      // Info states
      info: '#909399',
      draft: '#909399',
      accepted: '#409eff',
      abandoned: '#909399',
      // Default
      in_progress: '#409eff',
      outdated: '#e6a23c',
    };
    return colors[state] || '#909399';
  };

  /**
   * Get all available states for a context.
   * @returns {Array<{value: string, label: string, type: string}>}
   */
  const getAvailableStates = () => {
    const stateMap = getStateMap();
    return Object.entries(stateMap).map(([value, type]) => ({
      value,
      label: formatState(value),
      type,
    }));
  };

  /**
   * Check if a state is considered "active" or "in-progress".
   * @param {string} state - The state value
   * @returns {boolean}
   */
  const isActiveState = (state) => {
    const activeStates = ['pending', 'accepted', 'in_progress', 'replenishing', 'review'];
    return activeStates.includes(state);
  };

  /**
   * Check if a state is considered "final" or "completed".
   * @param {string} state - The state value
   * @returns {boolean}
   */
  const isFinalState = (state) => {
    const finalStates = ['completed', 'declined', 'abandoned', 'closed', 'checked'];
    return finalStates.includes(state);
  };

  return {
    getStateType,
    formatState,
    getStateColor,
    getAvailableStates,
    isActiveState,
    isFinalState,
  };
}

export default useStateType;
