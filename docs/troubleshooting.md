# Troubleshooting

- **Empty content downloads**: Ensure the RSS link is valid; the tool automatically triggers conversion with a 2-second delay.
- **HTTP errors**: Check network connectivity or subsite availability. Increase threads cautiously to avoid rate limiting.
- **Evid format issues**: Verify LaTeX dependencies if compiling manually.
- **RSS parsing failures**: Validate RSS file format; use sample files from `tests/data/` for testing. Ensure the RSS file contains valid HUDOC URLs for subsite detection.

For more issues, check logs or open an issue on the repository.
