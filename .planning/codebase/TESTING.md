# Testing
*Last updated: 2026-06-27*

## Testing Frameworks
- Currently, there are NO automated testing frameworks (e.g., `pytest`, `jest`) integrated or configured.
- The repository relies entirely on manual "run and verify" (Developer UI testing) strategies at this stage. 
- LLM response pipelines, markdown chunking, and database persistence are highly non-deterministic, making them difficult to unit test without rigorous mocking.

## Future Recommendations
- Integrate `pytest` for backend semantic logic and graph traversal validations.
- Integrate a headless browser testing suite (e.g., Playwright) to validate the integration between the Three.js 3D space and the 2D billboard components under WebGL conditions.
