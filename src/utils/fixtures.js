/**
 * INFOLENS DEVELOPMENT FIXTURES
 * Explicitly identified fallback data used ONLY when VITE_USE_FIXTURES=true or backend is unavailable.
 * Isolated from production API integration layer per team boundaries.
 */

export const DEV_USER = {
  id: 'usr_dev_101',
  email: 'researcher@infolens.edu',
  fullName: 'Dr. Sarah Lin',
  role: 'Academic Researcher',
  institution: 'Department of Computer Science',
  createdAt: '2026-01-15T08:30:00Z',
};

export const DEV_DOCUMENTS = [
  {
    id: 'doc_rag_2026',
    title: 'Retrieval_Augmented_Generation_Survey.pdf',
    filename: 'Retrieval_Augmented_Generation_Survey.pdf',
    fileType: 'PDF',
    fileSize: 4280192, // 4.1 MB
    uploadDate: '2026-10-07T14:20:00Z',
    status: 'Ready', // Options: Selected, Uploading, Uploaded, Processing, Ready, Failed
    pageCount: 18,
    extractedText: `Abstract: Retrieval-Augmented Generation (RAG) combines dense retriever models with generative language models to ground generation on external domain-specific knowledge bases. In this survey, we review vector indexing strategies, semantic chunking, re-ranking algorithms, and hallucination reduction mechanisms...
Section 1: Introduction. Large language models (LLMs) often suffer from parametric memory limitations and hallucinations. RAG addresses this by retrieving passages from indexed document collections using approximate nearest neighbor (ANN) search over embeddings...
Section 2: Architecture & Vector Embeddings. Documents are split into semantic chunks (e.g. 512 tokens with 50-token overlap). Embeddings are generated using dense encoders (e.g., text-embedding-3-small, BGE-large) and indexed in HNSW or FAISS vector spaces...
Section 3: Citation & Groundedness. To ensure auditability, RAG systems construct context prompts linking answer claims directly to source chunk IDs and page references...`,
  },
  {
    id: 'doc_quantum_002',
    title: 'Quantum_Computing_Principles_Ch4.docx',
    filename: 'Quantum_Computing_Principles_Ch4.docx',
    fileType: 'DOCX',
    fileSize: 1845000, // 1.7 MB
    uploadDate: '2026-10-08T09:15:00Z',
    status: 'Ready',
    pageCount: 12,
    extractedText: `Chapter 4: Superposition and Quantum Gates.
Quantum bits (qubits) differ fundamentally from classical bits by existing in linear combinations of states |0⟩ and |1⟩ until measured. Single-qubit operations are represented by unitary matrices such as Hadamard (H), Pauli-X, Pauli-Y, and Pauli-Z gates...
Entanglement is demonstrated through Bell states created by applying a Hadamard gate followed by a Controlled-NOT (CNOT) gate...`,
  },
  {
    id: 'doc_ml_notes_003',
    title: 'Lecture_Notes_Transformers_Attention.txt',
    filename: 'Lecture_Notes_Transformers_Attention.txt',
    fileType: 'TXT',
    fileSize: 345000, // 345 KB
    uploadDate: '2026-10-09T08:00:00Z',
    status: 'Ready',
    pageCount: 5,
    extractedText: `Lecture 7: Scaled Dot-Product Attention & Self-Attention Mechanics.
Self-Attention computes compatibility scores between Query (Q), Key (K), and Value (V) matrices:
Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V
Multi-Head Attention projects Q, K, V into h distinct subspaces allowing the model to jointly attend to information from different representation subspaces...`,
  }
];

export const DEV_CONVERSATIONS = [
  {
    id: 'conv_101',
    title: 'RAG Architecture & Chunking Strategies',
    documentId: 'doc_rag_2026',
    documentTitle: 'Retrieval_Augmented_Generation_Survey.pdf',
    updatedAt: '2026-10-09T09:45:00Z',
    messages: [
      {
        id: 'msg_1',
        sender: 'user',
        text: 'How does semantic chunking improve retrieval accuracy compared to fixed-length chunking?',
        timestamp: '2026-10-09T09:44:10Z'
      },
      {
        id: 'msg_2',
        sender: 'assistant',
        text: 'According to the uploaded survey document, semantic chunking preserves complete contextual boundaries and logical paragraph structures. Unlike rigid fixed-token windows, semantic chunking prevents key sentence concepts from being split across chunk boundaries, resulting in higher cosine similarity precision during dense retrieval.',
        timestamp: '2026-10-09T09:44:15Z',
        citations: [
          {
            id: 'cit_1',
            documentId: 'doc_rag_2026',
            documentTitle: 'Retrieval_Augmented_Generation_Survey.pdf',
            page: 4,
            passage: 'Documents are split into semantic chunks... semantic chunking prevents key sentence concepts from being split across chunk boundaries, resulting in higher cosine similarity precision.',
            sourceId: 'chunk_rag_p4_sec2'
          }
        ]
      }
    ]
  }
];

export const DEV_SUMMARIES = {
  'doc_rag_2026': {
    documentId: 'doc_rag_2026',
    documentTitle: 'Retrieval_Augmented_Generation_Survey.pdf',
    shortOverview: 'A comprehensive technical survey covering Retrieval-Augmented Generation (RAG) paradigms, vector indexing techniques, semantic chunking, and verifiable source citation frameworks.',
    detailedSummary: `### Executive Summary
This paper outlines the architectural evolution of Retrieval-Augmented Generation (RAG) in academic research and enterprise systems.

### Key Takeaways
1. **Hybrid Retrieval**: Combining BM25 keyword search with dense vector embeddings improves retrieval recall by up to 24%.
2. **Semantic Chunking**: Context-aware boundary splitting preserves topic coherence better than strict 512-token windows.
3. **Auditable Grounding**: Embedding explicit chunk references and page indices enables direct verification of model outputs against source material.

### Methodological Recommendations
- Use overlap windows of 10-15% when semantic boundary detection is unavailable.
- Implement re-ranking (e.g. Cohere Rerank or BGE-Reranker) before prompt assembly.`,
    citations: [
      { page: 1, passage: 'RAG combines dense retriever models with generative language models...' },
      { page: 4, passage: 'Hybrid retrieval improves recall across specialized domain vocabulary.' }
    ]
  }
};

export const DEV_QUESTIONS = [
  {
    id: 'q_1',
    type: 'multiple_choice',
    question: 'What formula expresses Scaled Dot-Product Attention in Transformer architectures?',
    options: [
      'Attention(Q, K, V) = sigmoid(Q * K^T) * V',
      'Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V',
      'Attention(Q, K, V) = relu(Q + K) * V',
      'Attention(Q, K, V) = (Q * V) / K'
    ],
    correctAnswer: 'Attention(Q, K, V) = softmax( (Q * K^T) / sqrt(d_k) ) * V',
    explanation: 'As defined in Vaswani et al. and documented in Section 2, scaling by 1/sqrt(d_k) prevents large dot-product magnitudes from pushing softmax into regions with extremely small gradients.'
  },
  {
    id: 'q_2',
    type: 'true_false',
    question: 'Semantic chunking relies strictly on fixed 512-token character limits without considering sentence boundaries.',
    options: ['True', 'False'],
    correctAnswer: 'False',
    explanation: 'Semantic chunking dynamically identifies paragraph and sentence boundaries to maintain coherent meaning rather than cutting off arbitrarily at 512 tokens.'
  },
  {
    id: 'q_3',
    type: 'short_answer',
    question: 'What two quantum logic gates are commonly used to generate a maximally entangled Bell state?',
    correctAnswer: 'Hadamard (H) gate and Controlled-NOT (CNOT) gate.',
    explanation: 'Applying an H gate to the control qubit places it in equal superposition, and the subsequent CNOT gate entangles the target qubit.'
  }
];

export const DEV_FLASHCARDS = [
  {
    id: 'fc_1',
    front: 'What is Retrieval-Augmented Generation (RAG)?',
    back: 'A framework that combines dense vector retrieval from an external knowledge base with a generative language model to produce grounded, verifiable answers.',
    known: false
  },
  {
    id: 'fc_2',
    front: 'What is the purpose of scaling by 1 / sqrt(d_k) in dot-product attention?',
    back: 'It prevents dot products from growing excessively large for high dimensions, which would cause softmax gradients to vanish.',
    known: false
  },
  {
    id: 'fc_3',
    front: 'What is a Bell State in Quantum Computing?',
    back: 'A maximally entangled quantum state of two qubits, typically generated using a Hadamard gate followed by a CNOT gate.',
    known: false
  }
];
