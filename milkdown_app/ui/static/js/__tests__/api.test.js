import { describe, it, expect, vi } from 'vitest'

describe('Frontend API Contracts', () => {

  describe('Chat Stream Parsing', () => {
    it('should handle SSE chat stream and emit tokens', async () => {
      // Mock fetch for the SSE endpoint
      const mockStream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode('data: {"type": "token", "content": "Hello"}\n\n'));
          controller.enqueue(new TextEncoder().encode('data: {"type": "graph_update", "nodes": []}\n\n'));
          controller.close();
        }
      });
      
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        body: mockStream
      });

      const response = await fetch('/api/chat/stream', { method: 'POST' });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let tokensReceived = [];
      let graphUpdates = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'token') {
              tokensReceived.push(data.content);
            } else if (data.type === 'graph_update') {
              graphUpdates++;
            }
          }
        }
      }
      
      expect(tokensReceived.length).toBe(1);
      expect(tokensReceived[0]).toBe('Hello');
      expect(graphUpdates).toBe(1);
    })
  })

})
