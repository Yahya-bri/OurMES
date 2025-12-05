/**
 * Async action composable for managing loading states and error handling.
 *
 * Usage:
 *   import { useAsyncAction } from '@/shared/composables/useAsyncAction';
 *   const { execute, loading, error, reset } = useAsyncAction();
 *
 *   const handleSave = () => execute(async () => {
 *     await saveData();
 *     ElMessage.success('Saved!');
 *   }, 'Failed to save');
 */
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

export function useAsyncAction(options = {}) {
  const loading = ref(false);
  const error = ref(null);
  const showErrorMessage = options.showErrorMessage !== false;

  /**
   * Execute an async action with loading state management.
   * @param {Function} action - Async function to execute
   * @param {string} errorMessage - Default error message if action fails
   * @returns {Promise<any>} Result of the action
   */
  const execute = async (action, errorMessage = 'An error occurred') => {
    loading.value = true;
    error.value = null;

    try {
      const result = await action();
      return result;
    } catch (err) {
      error.value = err;
      const message = err.response?.data?.error || err.message || errorMessage;

      if (showErrorMessage) {
        ElMessage.error(message);
      }

      console.error(errorMessage, err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Execute with success message.
   * @param {Function} action - Async function to execute
   * @param {string} successMessage - Message to show on success
   * @param {string} errorMessage - Default error message if action fails
   * @returns {Promise<any>}
   */
  const executeWithSuccess = async (action, successMessage, errorMessage = 'An error occurred') => {
    const result = await execute(action, errorMessage);
    ElMessage.success(successMessage);
    return result;
  };

  /**
   * Reset error state.
   */
  const reset = () => {
    error.value = null;
    loading.value = false;
  };

  return {
    loading,
    error,
    execute,
    executeWithSuccess,
    reset,
  };
}

/**
 * Create multiple named loading states.
 *
 * Usage:
 *   const { isLoading, startLoading, stopLoading, withLoading } = useMultipleLoading();
 *   startLoading('save');
 *   await saveData();
 *   stopLoading('save');
 */
export function useMultipleLoading() {
  const loadingStates = ref({});

  const isLoading = (key) => !!loadingStates.value[key];

  const startLoading = (key) => {
    loadingStates.value[key] = true;
  };

  const stopLoading = (key) => {
    loadingStates.value[key] = false;
  };

  const withLoading = async (key, action) => {
    startLoading(key);
    try {
      return await action();
    } finally {
      stopLoading(key);
    }
  };

  return {
    loadingStates,
    isLoading,
    startLoading,
    stopLoading,
    withLoading,
  };
}

export default useAsyncAction;
