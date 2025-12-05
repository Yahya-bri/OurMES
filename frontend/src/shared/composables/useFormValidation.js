/**
 * Form validation composable providing reusable validation rules.
 *
 * Usage:
 *   import { useFormValidation } from '@/shared/composables/useFormValidation';
 *   const { required, positiveNumber, email, maxLength } = useFormValidation();
 *
 *   const rules = {
 *     name: [required('Name')],
 *     quantity: [required('Quantity'), positiveNumber()],
 *     email: [email()],
 *   };
 */

export function useFormValidation() {
  /**
   * Required field validator.
   * @param {string} fieldLabel - Human readable field name
   * @param {string} trigger - Validation trigger ('blur', 'change')
   * @returns {object} Validation rule
   */
  const required = (fieldLabel = 'This field', trigger = 'blur') => ({
    required: true,
    message: `${fieldLabel} is required`,
    trigger,
  });

  /**
   * Positive number validator.
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const positiveNumber = (fieldLabel = 'Value') => ({
    validator: (rule, value, callback) => {
      if (value === null || value === undefined || value === '') {
        return callback();
      }
      const num = Number(value);
      if (isNaN(num) || num <= 0) {
        return callback(new Error(`${fieldLabel} must be a positive number`));
      }
      callback();
    },
    trigger: 'blur',
  });

  /**
   * Non-negative number validator.
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const nonNegativeNumber = (fieldLabel = 'Value') => ({
    validator: (rule, value, callback) => {
      if (value === null || value === undefined || value === '') {
        return callback();
      }
      const num = Number(value);
      if (isNaN(num) || num < 0) {
        return callback(new Error(`${fieldLabel} cannot be negative`));
      }
      callback();
    },
    trigger: 'blur',
  });

  /**
   * Email validator.
   * @returns {object} Validation rule
   */
  const email = () => ({
    type: 'email',
    message: 'Please enter a valid email address',
    trigger: 'blur',
  });

  /**
   * Maximum length validator.
   * @param {number} max - Maximum length
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const maxLength = (max, fieldLabel = 'This field') => ({
    max,
    message: `${fieldLabel} cannot exceed ${max} characters`,
    trigger: 'blur',
  });

  /**
   * Minimum length validator.
   * @param {number} min - Minimum length
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const minLength = (min, fieldLabel = 'This field') => ({
    min,
    message: `${fieldLabel} must be at least ${min} characters`,
    trigger: 'blur',
  });

  /**
   * Pattern validator.
   * @param {RegExp} pattern - Regular expression pattern
   * @param {string} message - Error message
   * @returns {object} Validation rule
   */
  const pattern = (pattern, message = 'Invalid format') => ({
    pattern,
    message,
    trigger: 'blur',
  });

  /**
   * Range validator for numbers.
   * @param {number} min - Minimum value
   * @param {number} max - Maximum value
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const numberRange = (min, max, fieldLabel = 'Value') => ({
    validator: (rule, value, callback) => {
      if (value === null || value === undefined || value === '') {
        return callback();
      }
      const num = Number(value);
      if (isNaN(num)) {
        return callback(new Error(`${fieldLabel} must be a number`));
      }
      if (num < min || num > max) {
        return callback(new Error(`${fieldLabel} must be between ${min} and ${max}`));
      }
      callback();
    },
    trigger: 'blur',
  });

  /**
   * URL validator.
   * @returns {object} Validation rule
   */
  const url = () => ({
    type: 'url',
    message: 'Please enter a valid URL',
    trigger: 'blur',
  });

  /**
   * Phone number validator (basic).
   * @returns {object} Validation rule
   */
  const phone = () => ({
    pattern: /^[\d\s\-\+\(\)]+$/,
    message: 'Please enter a valid phone number',
    trigger: 'blur',
  });

  /**
   * Date in future validator.
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const futureDate = (fieldLabel = 'Date') => ({
    validator: (rule, value, callback) => {
      if (!value) return callback();
      const date = new Date(value);
      if (date <= new Date()) {
        return callback(new Error(`${fieldLabel} must be in the future`));
      }
      callback();
    },
    trigger: 'change',
  });

  /**
   * Date range validator.
   * @param {string} startField - Name of start date field in form
   * @param {string} endField - Name of end date field in form
   * @returns {object} Validation rule
   */
  const dateRange = (startField, endField) => ({
    validator: (rule, value, callback, source) => {
      const start = source[startField];
      const end = source[endField];
      if (start && end && new Date(start) > new Date(end)) {
        return callback(new Error('Start date must be before end date'));
      }
      callback();
    },
    trigger: 'change',
  });

  /**
   * Unique identifier pattern (alphanumeric with dashes).
   * @param {string} fieldLabel - Human readable field name
   * @returns {object} Validation rule
   */
  const identifier = (fieldLabel = 'ID') => ({
    pattern: /^[a-zA-Z0-9\-_]+$/,
    message: `${fieldLabel} can only contain letters, numbers, dashes, and underscores`,
    trigger: 'blur',
  });

  /**
   * Create common rules for an entity (number, name, description).
   * @param {string} entityName - Name of the entity (e.g., 'Order', 'Product')
   * @returns {object} Common validation rules object
   */
  const createEntityRules = (entityName) => ({
    number: [required(`${entityName} number`), maxLength(255, 'Number')],
    name: [required(`${entityName} name`), maxLength(1024, 'Name')],
    description: [maxLength(2048, 'Description')],
  });

  return {
    required,
    positiveNumber,
    nonNegativeNumber,
    email,
    maxLength,
    minLength,
    pattern,
    numberRange,
    url,
    phone,
    futureDate,
    dateRange,
    identifier,
    createEntityRules,
  };
}

export default useFormValidation;
