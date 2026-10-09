import { describe, it, expect } from 'vitest';
import { documentApi } from '../api/documentApi';
import { chatApi } from '../api/chatApi';

describe('Centralized API Layer & Fixture Integration', () => {
  it('retrieves documents list cleanly', async () => {
    const docs = await documentApi.getDocuments();
    expect(Array.isArray(docs)).toBe(true);
    expect(docs.length).toBeGreaterThan(0);
    expect(docs[0]).toHaveProperty('title');
    expect(docs[0]).toHaveProperty('status');
  });

  it('handles chat conversation creation and message sending', async () => {
    const docs = await documentApi.getDocuments();
    const docId = docs[0].id;

    const conv = await chatApi.createConversation(docId, 'Test Conversation');
    expect(conv).toHaveProperty('id');
    expect(conv.title).toBe('Test Conversation');

    const messageRes = await chatApi.sendMessage(conv.id, 'What is the main finding?', docId);
    expect(messageRes.userMessage.text).toBe('What is the main finding?');
    expect(messageRes.assistantMessage.sender).toBe('assistant');
    expect(Array.isArray(messageRes.assistantMessage.citations)).toBe(true);
    expect(messageRes.assistantMessage.citations.length).toBeGreaterThan(0);
  });
});
