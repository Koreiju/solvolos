const { test, expect } = require('@playwright/test');
const { SSEProcessor } = require('../../static/js/billboard');

test('TDD-DIF-02: Fractured SSE JSON parsing buffer', () => {
  const processor = new SSEProcessor();
  
  // Pass deliberately fractured JSON string
  const chunk1 = '{"id": "c1", "te';
  const chunk2 = 'xt": "hello"}';
  
  // Parse first fractured chunk
  const res1 = processor.parse(chunk1);
  expect(res1).toHaveLength(0); // Should buffer and return nothing
  
  // Parse second chunk to complete it
  const res2 = processor.parse(chunk2);
  expect(res2).toHaveLength(1);
  expect(res2[0].id).toBe('c1');
  expect(res2[0].text).toBe('hello');
  
  // Test multiple mixed fractured objects
  const chunk3 = '{"id": "c2"} {"id":';
  const chunk4 = ' "c3", "value"';
  const chunk5 = ': "yes"} {"a": 1';
  const chunk6 = '}';
  
  const res3 = processor.parse(chunk3);
  expect(res3).toHaveLength(1);
  expect(res3[0].id).toBe('c2');
  
  const res4 = processor.parse(chunk4);
  expect(res4).toHaveLength(0);
  
  const res5 = processor.parse(chunk5);
  expect(res5).toHaveLength(1);
  expect(res5[0].id).toBe('c3');
  
  const res6 = processor.parse(chunk6);
  expect(res6).toHaveLength(1);
  expect(res6[0].a).toBe(1);
});
