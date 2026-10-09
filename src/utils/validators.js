/**
 * Input & File Validation Utilities for InfoLens
 */

export const SUPPORTED_FILE_EXTENSIONS = ['.pdf', '.docx', '.txt'];
export const SUPPORTED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'text/plain'
];
export const DEFAULT_MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB

export function validateFile(file, maxSizeBytes = DEFAULT_MAX_FILE_SIZE_BYTES) {
  if (!file) {
    return { valid: false, error: 'No file selected.' };
  }

  const filename = file.name || '';
  const extension = '.' + filename.split('.').pop().toLowerCase();

  const isExtensionValid = SUPPORTED_FILE_EXTENSIONS.includes(extension);
  const isMimeValid = !file.type || SUPPORTED_MIME_TYPES.includes(file.type);

  if (!isExtensionValid && !isMimeValid) {
    return {
      valid: false,
      error: `Unsupported file type "${extension || file.type}". Supported formats are PDF, DOCX, and TXT.`
    };
  }

  if (file.size > maxSizeBytes) {
    const maxSizeMB = Math.round(maxSizeBytes / (1024 * 1024));
    return {
      valid: false,
      error: `File size exceeds maximum limit of ${maxSizeMB} MB. Please upload a smaller file.`
    };
  }

  return { valid: true, error: null };
}

export function validateEmail(email) {
  if (!email) return 'Email is required';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) return 'Please enter a valid email address';
  return null;
}

export function validatePassword(password) {
  if (!password) return 'Password is required';
  if (password.length < 8) return 'Password must be at least 8 characters long';
  return null;
}
