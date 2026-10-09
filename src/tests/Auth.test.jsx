import { describe, it, expect } from 'vitest';
import { validateEmail, validatePassword, validateFile } from '../utils/validators';

describe('Validation Utilities', () => {
  it('validates email format correctly', () => {
    expect(validateEmail('invalid-email')).toBe('Please enter a valid email address');
    expect(validateEmail('')).toBe('Email is required');
    expect(validateEmail('valid.student@university.edu')).toBeNull();
  });

  it('validates password length correctly', () => {
    expect(validatePassword('short')).toBe('Password must be at least 8 characters long');
    expect(validatePassword('')).toBe('Password is required');
    expect(validatePassword('SecurePass123!')).toBeNull();
  });

  it('validates supported file types (PDF, DOCX, TXT)', () => {
    const validPdf = new File(['dummy content'], 'paper.pdf', { type: 'application/pdf' });
    const validDocx = new File(['dummy content'], 'notes.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const validTxt = new File(['dummy content'], 'lecture.txt', { type: 'text/plain' });
    const invalidExe = new File(['dummy content'], 'script.exe', { type: 'application/x-msdownload' });

    expect(validateFile(validPdf).valid).toBe(true);
    expect(validateFile(validDocx).valid).toBe(true);
    expect(validateFile(validTxt).valid).toBe(true);

    const invalidResult = validateFile(invalidExe);
    expect(invalidResult.valid).toBe(false);
    expect(invalidResult.error).toContain('Unsupported file type');
  });

  it('enforces maximum file size limit (25 MB)', () => {
    const oversizedFile = new File(['a'.repeat(100)], 'huge.pdf', { type: 'application/pdf' });
    Object.defineProperty(oversizedFile, 'size', { value: 30 * 1024 * 1024 }); // 30 MB

    const result = validateFile(oversizedFile);
    expect(result.valid).toBe(false);
    expect(result.error).toContain('File size exceeds maximum limit');
  });
});
